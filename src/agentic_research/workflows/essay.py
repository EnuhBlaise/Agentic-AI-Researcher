"""Workflow 1 - Reflection: draft an essay, critique it, then revise it."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ..llm import LLM

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class EssayResult:
    draft: str
    feedback: str
    revised: str


def run_essay(llm: LLM, topic: str) -> EssayResult:
    log.info("[1/3] Writing draft")
    draft = write_draft(llm, topic)

    log.info("[2/3] Reflecting on draft")
    feedback = reflect_on_draft(llm, draft)

    log.info("[3/3] Revising draft")
    revised = revise_draft(llm, draft, feedback)

    return EssayResult(draft=draft, feedback=feedback, revised=revised)


def write_draft(llm: LLM, topic: str) -> str:
    prompt = f"""Write a well-structured essay on the following topic.

Topic: {topic}

Requirements:
- Clear introduction with a thesis statement
- At least 4 paragraphs with logical development
- Balanced analysis with examples or evidence
- Strong conclusion that reinforces the main argument
- Polished academic writing style
- Return only the final essay text"""
    return llm.complete(prompt)


def reflect_on_draft(llm: LLM, draft: str) -> str:
    prompt = f"""Review the following essay draft and provide constructive feedback.

Focus on:
- overall structure and flow
- clarity and coherence
- strength of the argument or thesis
- quality of evidence and examples
- writing style and tone

Be critical but fair, and suggest specific improvements.

Essay draft:
{draft}"""
    return llm.complete(prompt)


def revise_draft(llm: LLM, draft: str, feedback: str) -> str:
    prompt = f"""Revise the original draft based on the feedback below.

Requirements:
- Preserve the original topic and central argument
- Address the issues raised in the feedback
- Improve structure, clarity, and coherence
- Strengthen reasoning and examples where needed
- Return only the revised essay text

Original draft:
{draft}

Feedback:
{feedback}"""
    return llm.complete(prompt)
