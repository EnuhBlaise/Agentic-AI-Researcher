"""Runtime settings, read once from environment variables (or a .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-4o-mini"


class ConfigError(RuntimeError):
    """Raised when a required setting is missing."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None
    tavily_api_key: str | None
    output_dir: Path


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError(
            "No API key found. Copy .env.example to .env and set LLM_API_KEY."
        )

    return Settings(
        api_key=api_key,
        model=os.getenv("LLM_MODEL") or DEFAULT_MODEL,
        base_url=os.getenv("LLM_BASE_URL") or None,
        tavily_api_key=os.getenv("TAVILY_API_KEY") or None,
        output_dir=Path(os.getenv("OUTPUT_DIR") or "outputs"),
    )
