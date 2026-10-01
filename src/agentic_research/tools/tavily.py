"""General web search through the Tavily API (needs TAVILY_API_KEY)."""

from __future__ import annotations

from .base import Tool
from .http import TIMEOUT_SECONDS, session

API_URL = "https://api.tavily.com/search"


def build_tavily_tool(api_key: str) -> Tool:
    def search_web(query: str, max_results: int = 5) -> list[dict]:
        response = session.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": query, "max_results": max_results},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return [
            {"title": hit.get("title", ""), "content": hit.get("content", ""), "url": hit.get("url", "")}
            for hit in response.json().get("results", [])
        ]

    return Tool(
        name="web_search",
        description="Search the web for recent, general information. Returns title, content and url.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords."},
                "max_results": {"type": "integer", "description": "How many results to return (default 5)."},
            },
            "required": ["query"],
        },
        run=search_web,
    )
