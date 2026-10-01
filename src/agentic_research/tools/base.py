"""What a tool is: a Python function plus the description the model sees."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema of the function's arguments
    run: Callable[..., list[dict]]

    def schema(self) -> dict:
        """The tool in the format the chat completions API expects."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
