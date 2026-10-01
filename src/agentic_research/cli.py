"""Command line entry point: `agentic-research <workflow> "<topic>"`."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

from .config import ConfigError, Settings, load_settings
from .llm import LLM
from .tools import build_tools
from .workflows import run_essay, run_report, run_team


def main() -> None:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        settings = load_settings()
    except ConfigError as error:
        sys.exit(f"Configuration error: {error}")

    llm = LLM(settings)
    folder = settings.output_dir / f"{args.workflow}-{_slugify(args.topic)}"

    if args.workflow == "essay":
        saved = _essay(llm, args.topic, folder)
    elif args.workflow == "report":
        saved = _report(llm, settings, args.topic, folder)
    else:
        saved = _team(llm, settings, args.topic, folder, args.max_steps)

    print("\nSaved:")
    for path in saved:
        print(f"  {path}")


def _essay(llm: LLM, topic: str, folder: Path) -> list[Path]:
    result = run_essay(llm, topic)
    return [
        _save(folder / "1_draft.md", result.draft),
        _save(folder / "2_feedback.md", result.feedback),
        _save(folder / "3_revised.md", result.revised),
    ]


def _report(llm: LLM, settings: Settings, topic: str, folder: Path) -> list[Path]:
    result = run_report(llm, build_tools(settings), topic)
    return [
        _save(folder / "1_preliminary_report.md", result.preliminary_report),
        _save(folder / "2_reflection.md", result.reflection),
        _save(folder / "3_revised_report.md", result.revised_report),
        _save(folder / "report.html", result.html),
    ]


def _team(llm: LLM, settings: Settings, topic: str, folder: Path, max_steps: int) -> list[Path]:
    result = run_team(llm, build_tools(settings), topic, max_steps=max_steps)
    saved = [
        _save(folder / f"step_{number}_{item.step.agent}.md", f"> {item.step.task}\n\n{item.output}")
        for number, item in enumerate(result.steps, start=1)
    ]
    saved.append(_save(folder / "report.md", result.final_report))
    return saved


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentic-research",
        description="Run an agentic LLM workflow on a topic.",
    )
    parser.add_argument(
        "workflow",
        choices=["essay", "report", "team"],
        help="essay: draft, reflect, revise | report: research with tools, "
        "reflect, HTML | team: planner + research/writer/editor agents",
    )
    parser.add_argument("topic", help="The topic or question to work on.")
    parser.add_argument(
        "--max-steps", type=int, default=5, help="Maximum plan length for 'team' (default 5)."
    )
    return parser.parse_args()


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "run"


def _save(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    main()
