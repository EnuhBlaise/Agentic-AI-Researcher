"""Workflow 3 - Multi-agent: a planner splits the job between three agents.

    planner  -> writes the plan (which agent does what, in order)
    research -> gathers information with the search tools
    writer   -> drafts text
    editor   -> critiques and revises

Each agent receives the output of all previous steps as context.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

from ..llm import LLM
from ..parsing import parse_json, strip_code_fence
from ..tools import Tool

log = logging.getLogger(__name__)

AGENT_NAMES = ("research", "writer", "editor")

WRITER_SYSTEM = (
    "You are a writing agent who produces clear, well-structured academic and "
    "technical content, grounded in the task and evidence you are given."
)
EDITOR_SYSTEM = (
    "You are an expert editor of academic and technical writing. Critique drafts "
    "for clarity, organization, evidence and style, and improve them while "
    "preserving the original intent."
)


@dataclass(frozen=True)
class PlanStep:
    agent: str
    task: str


@dataclass(frozen=True)
class StepResult:
    step: PlanStep
    output: str


@dataclass(frozen=True)
class TeamResult:
    steps: list[StepResult]

    @property
    def final_report(self) -> str:
        return strip_code_fence(self.steps[-1].output)


def run_team(llm: LLM, tools: list[Tool], topic: str, max_steps: int = 5) -> TeamResult:
    log.info("Planning")
    plan = make_plan(llm, topic, max_steps)

    results: list[StepResult] = []
    for number, step in enumerate(plan, start=1):
        log.info("[%d/%d] %s agent: %s", number, len(plan), step.agent, step.task)
        task = _add_context(step.task, results)
        output = _run_agent(llm, tools, step.agent, task)
        results.append(StepResult(step=step, output=output))

    return TeamResult(steps=results)


def make_plan(llm: LLM, topic: str, max_steps: int) -> list[PlanStep]:
    prompt = f"""You are a planning agent organizing a research workflow.

Available agents:
- "research": searches the web, Wikipedia and arXiv.
- "writer": drafts research text.
- "editor": reflects on drafts and revises them.

Write a step-by-step plan for the topic below, with at most {max_steps} steps.
Each step must be a single task for one agent. Include only research-related
tasks (search, summarize, draft, critique, revise). The final step must produce
the complete research report as a Markdown document.

Answer with a JSON list only, where each item looks like:
{{"agent": "research", "task": "..."}}

Topic: "{topic}\""""
    raw_steps = parse_json(llm.complete(prompt))

    plan = [PlanStep(agent=str(s["agent"]), task=str(s["task"])) for s in raw_steps]
    unknown = {step.agent for step in plan} - set(AGENT_NAMES)
    if not plan or unknown:
        raise ValueError(f"The planner returned an unusable plan: {raw_steps}")
    return plan[:max_steps]


def _run_agent(llm: LLM, tools: list[Tool], agent: str, task: str) -> str:
    if agent == "research":
        prompt = f"""You are a research assistant. Use the search tools to gather \
information, then report what you found with the source URLs.

Today's date: {date.today().isoformat()}

Task: {task}"""
        return llm.complete_with_tools(prompt, tools, max_turns=6)

    if agent == "writer":
        return llm.complete(task, system=WRITER_SYSTEM)

    return llm.complete(task, system=EDITOR_SYSTEM)


def _add_context(task: str, previous: list[StepResult]) -> str:
    """Prefix the task with the output of the steps already completed."""
    if not previous:
        return task

    context = "\n\n".join(
        f"--- Step {number} ({result.step.agent} agent) ---\n{result.output}"
        for number, result in enumerate(previous, start=1)
    )
    return f"""Work done so far:

{context}

Your task now:
{task}"""
