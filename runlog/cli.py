"""The command line: 'python -m runlog best', 'python -m runlog report', 'python -m runlog show' and 'python -m runlog models'."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date

from .data import Run, load_runs
from .report import format_models, format_row, format_run, markdown_summary, summary, top_runs

DEFAULT_DATA = "runs.csv"
SINCE_HELP = "keep only the runs from DATE on, DATE included, written YYYY-MM-DD"
MODEL_HELP = "keep only the runs of model NAME"


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


def runs_of_model(runs: list[Run], model: str) -> list[Run]:
    """The runs of this model, in file order, the name lowercased first. Raises ValueError when none are left."""
    name = model.lower()
    kept = [run for run in runs if run.model == name]
    if not kept:
        raise ValueError(f"no runs of model {name!r}")
    return kept


def runs_with_min_epochs(runs: list[Run], min_epochs: int) -> list[Run]:
    """The runs with at least min_epochs epochs, in file order. Raises ValueError when none are left."""
    kept = [run for run in runs if run.epochs >= min_epochs]
    if not kept:
        raise ValueError(f"no runs with at least {min_epochs} epochs")
    return kept


def find_row(path: str, run_id: str) -> dict[str, str]:
    """The first row of the CSV at path with this run_id, every column as written, in file order.

    Raises ValueError when no row has that id.
    """
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("run_id") == run_id:
                return row
    raise ValueError(f"no run with id {run_id!r} in {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="runlog", description="Look through a log of training runs.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="the CSV of runs, runs.csv by default")
    commands = parser.add_subparsers(dest="command", required=True)
    best = commands.add_parser("best", help="print the run with the highest validation accuracy")
    best.add_argument("--top", type=int, default=1, metavar="N", help="print the N best runs, highest first")
    best.add_argument("--since", metavar="DATE", help=SINCE_HELP)
    best.add_argument("--model", metavar="NAME", help=MODEL_HELP)
    best.add_argument("--min-epochs", type=int, metavar="N", help="keep only the runs with at least N epochs")
    report = commands.add_parser("report", help="print a summary of every run")
    report.add_argument("--format", choices=["text", "md"], default="text", help="print the report as text or as Markdown")
    report.add_argument("--since", metavar="DATE", help=SINCE_HELP)
    report.add_argument("--model", metavar="NAME", help=MODEL_HELP)
    show = commands.add_parser("show", help="print one run in full, one column per line")
    show.add_argument("run_id", metavar="RUN_ID", help="the id of the run to print")
    commands.add_parser("models", help="print every model and its number of runs, sorted by name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "show":
            row = find_row(args.data, args.run_id)
        elif args.command == "models":
            runs = load_runs(args.data)
            if not runs:
                raise ValueError(f"no runs in {args.data}")
            text = format_models(runs)
        else:
            runs = load_runs(args.data)
            if args.since is not None:
                runs = runs_since(runs, parse_since(args.since))
            if args.model is not None:
                runs = runs_of_model(runs, args.model)
            if args.command == "best":
                if args.min_epochs is not None:
                    runs = runs_with_min_epochs(runs, args.min_epochs)
                ranked = top_runs(runs, args.top)
            else:
                text = markdown_summary(runs) if args.format == "md" else summary(runs)
    except (OSError, ValueError) as exc:
        print(f"runlog: {exc}", file=sys.stderr)
        return 1
    if args.command == "show":
        print(format_row(row))
    elif args.command == "best":
        for run in ranked:
            print(format_run(run))
    else:
        print(text)
    return 0
