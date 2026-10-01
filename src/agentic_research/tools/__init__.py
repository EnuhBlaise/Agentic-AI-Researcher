"""Search tools the agents can call.

To add a tool: write a function, wrap it in a `Tool`, and add it to
`build_tools` below. Nothing else needs to change.
"""

from __future__ import annotations

from ..config import Settings
from .arxiv import arxiv_tool
from .base import Tool
from .tavily import build_tavily_tool
from .wikipedia import wikipedia_tool

__all__ = ["Tool", "build_tools"]


def build_tools(settings: Settings) -> list[Tool]:
    """Return the tools available with the current settings."""
    tools = [arxiv_tool, wikipedia_tool]
    if settings.tavily_api_key:
        tools.append(build_tavily_tool(settings.tavily_api_key))
    return tools
