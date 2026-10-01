"""Helpers for cleaning up text returned by the model."""

from __future__ import annotations

import json
import re

_FENCE = re.compile(r"^```[a-zA-Z]*\n?|\n?```$")


def strip_code_fence(text: str) -> str:
    """Remove a surrounding ```...``` block, which models often add."""
    return _FENCE.sub("", text.strip()).strip()


def parse_json(text: str):
    """Parse JSON from a model answer, tolerating code fences and stray prose."""
    cleaned = strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fall back to the first {...} or [...] block found in the text.
    match = re.search(r"\{.*\}|\[.*\]", cleaned, flags=re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"The model did not return valid JSON:\n{text[:500]}")
