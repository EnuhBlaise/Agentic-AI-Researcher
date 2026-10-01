"""Search academic papers on arXiv (public API, no key needed)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from .base import Tool
from .http import TIMEOUT_SECONDS, session

API_URL = "https://export.arxiv.org/api/query"
ATOM = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    response = session.get(
        API_URL,
        params={"search_query": f"all:{query}", "max_results": max_results},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    papers = []
    for entry in ET.fromstring(response.content).findall("atom:entry", ATOM):
        pdf_links = [
            link.get("href")
            for link in entry.findall("atom:link", ATOM)
            if link.get("title") == "pdf"
        ]
        papers.append(
            {
                "title": " ".join(entry.findtext("atom:title", "", ATOM).split()),
                "url": entry.findtext("atom:id", "", ATOM),
                "summary": " ".join(entry.findtext("atom:summary", "", ATOM).split()),
                "published": entry.findtext("atom:published", "", ATOM)[:10],
                "link_pdf": pdf_links[0] if pdf_links else None,
            }
        )
    return papers


arxiv_tool = Tool(
    name="arxiv_search",
    description=(
        "Search arXiv for research papers. Returns title, url, summary, "
        "publication date and PDF link for each paper."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search keywords."},
            "max_results": {"type": "integer", "description": "How many papers to return (default 5)."},
        },
        "required": ["query"],
    },
    run=search_arxiv,
)
