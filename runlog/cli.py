"""The command line: 'python -m runlog best' and 'python -m runlog report'."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date

from .data import Run, load_runs
from .report import format_run, markdown_summary, summary, top_runs

DEFAULT_DATA = "runs.csv"
SINCE_HELP = "keep only the runs from DATE on, DATE included, written YYYY-MM-DD"


def parse_since(text: str) -> str:
    """The --since DATE as YYYY-MM-DD. Raises ValueError when it is not a real date in that form."""
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            raise ValueError
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValueError(f"--since needs a date written YYYY-MM-DD, not {text!r}") from None


def runs_since(runs: list[Run], since: str) -> list[Run]:
    """The runs dated since or later, in file order. Raises ValueError when none are left."""
    kept = [run for run in runs if run.date >= since]
    if not kept:
        raise ValueError(f"no runs on or after {since}")
    return kept


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runlog", description="Look through a log of training runs.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="the CSV of runs, runs.csv by default")
    commands = parser.add_subparsers(dest="command", required=True)
    best = commands.add_parser("best", help="print the run with the highest validation accuracy")
    best.add_argument("--top", type=int, default=1, metavar="N", help="print the N best runs, highest first")
    best.add_argument("--since", metavar="DATE", help=SINCE_HELP)
    report = commands.add_parser("report", help="print a summary of every run")
    report.add_argument("--format", choices=["text", "md"], default="text", help="print the report as text or as Markdown")
    report.add_argument("--since", metavar="DATE", help=SINCE_HELP)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runs = load_runs(args.data)
        if args.since is not None:
            runs = runs_since(runs, parse_since(args.since))
    except (OSError, ValueError) as exc:
        print(f"runlog: {exc}", file=sys.stderr)
        return 1
    if args.command == "best":
        try:
            ranked = top_runs(runs, args.top)
        except ValueError as exc:
            print(f"runlog: {exc}", file=sys.stderr)
            return 1
        for run in ranked:
            print(format_run(run))
    elif args.command == "report":
        print(markdown_summary(runs) if args.format == "md" else summary(runs))
    return 0
