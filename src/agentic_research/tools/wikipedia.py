"""Look up an article summary on Wikipedia (public API, no key needed)."""

from __future__ import annotations

from urllib.parse import quote

from .base import Tool
from .http import TIMEOUT_SECONDS, session

SEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"


def search_wikipedia(query: str) -> list[dict]:
    # Step 1: find the best matching article title.
    search = session.get(
        SEARCH_URL,
        params={"action": "query", "list": "search", "srsearch": query, "srlimit": 1, "format": "json"},
        timeout=TIMEOUT_SECONDS,
    )
    search.raise_for_status()
    hits = search.json()["query"]["search"]
    if not hits:
        return [{"error": f"No Wikipedia article found for '{query}'."}]

    # Step 2: fetch that article's summary.
    title = hits[0]["title"]
    summary = session.get(
        SUMMARY_URL.format(title=quote(title.replace(" ", "_"), safe="")),
        timeout=TIMEOUT_SECONDS,
    )
    summary.raise_for_status()
    page = summary.json()

    return [
        {
            "title": page.get("title", title),
            "summary": page.get("extract", ""),
            "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    ]


wikipedia_tool = Tool(
    name="wikipedia_search",
    description="Get the summary of the Wikipedia article that best matches a query.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Topic to look up."},
        },
        "required": ["query"],
    },
    run=search_wikipedia,
)
