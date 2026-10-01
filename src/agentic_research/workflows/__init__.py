"""One module per workflow. Each exposes a single `run_*` function."""

from .essay import EssayResult, run_essay
from .report import ReportResult, run_report
from .team import TeamResult, run_team

__all__ = ["EssayResult", "ReportResult", "TeamResult", "run_essay", "run_report", "run_team"]
