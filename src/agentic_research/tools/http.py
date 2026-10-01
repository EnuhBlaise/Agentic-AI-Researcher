"""Shared HTTP session with retries for the search tools."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIMEOUT_SECONDS = 30
USER_AGENT = "agentic-research/0.1 (https://github.com/; educational project)"


def build_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
    )
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


session = build_session()
