"""The only module that talks to the LLM API.

Everything else calls `LLM.complete` (plain text in, text out) or
`LLM.complete_with_tools` (the model may call tools before answering).
"""

from __future__ import annotations

import json
import logging

from openai import OpenAI

from .config import Settings
from .tools import Tool

log = logging.getLogger(__name__)


class LLM:
    def __init__(self, settings: Settings) -> None:
        self.model = settings.model
        self._client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Send one prompt and return the model's text answer."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=_build_messages(prompt, system),
        )
        return (response.choices[0].message.content or "").strip()

    def complete_with_tools(
        self,
        prompt: str,
        tools: list[Tool],
        *,
        system: str | None = None,
        max_turns: int = 8,
    ) -> str:
        """Let the model call tools in a loop until it writes a final answer.

        Each turn: ask the model -> if it requested tools, run them and feed
        the results back -> repeat. The loop ends when the model answers
        without requesting a tool, or after `max_turns`.
        """
        tools_by_name = {tool.name: tool for tool in tools}
        schemas = [tool.schema() for tool in tools]
        messages = _build_messages(prompt, system)

        for _ in range(max_turns):
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message
            messages.append(message)

            if not message.tool_calls:
                return (message.content or "").strip()

            for call in message.tool_calls:
                result = _run_tool_call(tools_by_name, call.function.name, call.function.arguments)
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}
                )

        # Out of turns: ask for a final answer from what was gathered so far.
        messages.append(
            {"role": "user", "content": "Stop searching and write your final answer now."}
        )
        response = self._client.chat.completions.create(model=self.model, messages=messages)
        return (response.choices[0].message.content or "").strip()


def _build_messages(prompt: str, system: str | None) -> list:
    messages: list = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


def _run_tool_call(tools_by_name: dict[str, Tool], name: str, raw_arguments: str):
    """Run one tool call. Errors are returned to the model, never raised."""
    log.info("    tool: %s(%s)", name, raw_arguments)
    try:
        arguments = json.loads(raw_arguments or "{}")
        return tools_by_name[name].run(**arguments)
    except Exception as error:  # the model can recover if it sees the error
        return [{"error": f"{type(error).__name__}: {error}"}]
