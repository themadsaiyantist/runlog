"""The command line: 'python -m runlog best' and 'python -m runlog report'."""

from __future__ import annotations

import argparse
import sys

from .data import load_runs
from .report import format_run, markdown_summary, summary, top_runs

DEFAULT_DATA = "runs.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runlog", description="Look through a log of training runs.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="the CSV of runs, runs.csv by default")
    commands = parser.add_subparsers(dest="command", required=True)
    best = commands.add_parser("best", help="print the run with the highest validation accuracy")
    best.add_argument("--top", type=int, default=1, metavar="N", help="print the N best runs, highest first")
    report = commands.add_parser("report", help="print a summary of every run")
    report.add_argument("--format", choices=["text", "md"], default="text", help="print the report as text or as Markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runs = load_runs(args.data)
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
