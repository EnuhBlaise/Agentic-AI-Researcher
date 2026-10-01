"""Workflow 2 - Tool use: research with search tools, reflect, publish as HTML."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ..llm import LLM
from ..parsing import parse_json, strip_code_fence
from ..tools import Tool

log = logging.getLogger(__name__)

RESEARCHER_SYSTEM = """You are a research assistant who writes detailed, accurate, \
properly sourced research reports.

- Use the search tools to find papers and web content before writing.
- Cite sources and include their full URLs. Only cite sources the tools returned.
- Use an academic tone and organize the report into clearly labeled sections.
- Never write placeholders such as "(citation needed)"."""


@dataclass(frozen=True)
class ReportResult:
    preliminary_report: str
    reflection: str
    revised_report: str
    html: str


def run_report(llm: LLM, tools: list[Tool], topic: str) -> ReportResult:
    log.info("[1/3] Researching with tools")
    preliminary = research(llm, tools, topic)

    log.info("[2/3] Reflecting and rewriting")
    reflection, revised = reflect_and_rewrite(llm, preliminary)

    log.info("[3/3] Converting to HTML")
    html = convert_to_html(llm, revised)

    return ReportResult(
        preliminary_report=preliminary,
        reflection=reflection,
        revised_report=revised,
        html=html,
    )


def research(llm: LLM, tools: list[Tool], topic: str) -> str:
    return llm.complete_with_tools(topic, tools, system=RESEARCHER_SYSTEM, max_turns=10)


def reflect_and_rewrite(llm: LLM, report: str) -> tuple[str, str]:
    """Return (reflection, revised_report)."""
    prompt = f"""Review the report below and answer with valid JSON only, using exactly \
these keys: "reflection" and "revised_report". Both values must be strings.

- "reflection": a concise academic review covering Strengths, Limitations, \
Suggestions, and Opportunities.
- "revised_report": the report rewritten in a clearer, more polished academic \
style. Keep the substance, every citation and every URL.

REPORT:
{report}"""
    answer = llm.complete(prompt, system="You are an academic reviewer and editor.")
    data = parse_json(answer)
    return str(data["reflection"]).strip(), str(data["revised_report"]).strip()


def convert_to_html(llm: LLM, report: str) -> str:
    prompt = f"""Convert the report below into a complete, clean HTML document.

- Return only HTML: no markdown fences and no commentary.
- Use semantic HTML with a title, sections and paragraphs.
- Add a small embedded stylesheet so the page is pleasant to read.
- Turn every URL into a clickable link.

REPORT:
{report}"""
    answer = llm.complete(prompt, system="You convert plain text reports into HTML documents.")
    return strip_code_fence(answer)
