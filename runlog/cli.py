"""The command line: 'python -m runlog best' and 'python -m runlog report'."""

from __future__ import annotations

import argparse
import sys

from .data import load_runs
from .report import best_run, format_run, summary

DEFAULT_DATA = "runs.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runlog", description="Look through a log of training runs.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="the CSV of runs, runs.csv by default")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("best", help="print the run with the highest validation accuracy")
    commands.add_parser("report", help="print a summary of every run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runs = load_runs(args.data)
    except (OSError, ValueError) as exc:
        print(f"runlog: {exc}", file=sys.stderr)
        return 1
    if args.command == "best":
        print(format_run(best_run(runs)))
    elif args.command == "report":
        print(summary(runs))
    return 0
