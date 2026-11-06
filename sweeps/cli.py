"""The command line: expand, run and report."""

from __future__ import annotations

import argparse
import time

from .config import load
from .grid import expand
from .log import say
from .report import summary
from .runner import run_all
from .timing import fmt_seconds
from .writer import write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sweeps", description="Run a grid of training settings.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, text in [("expand", "print every configuration"), ("run", "run every configuration and write the CSV")]:
        command = commands.add_parser(name, help=text)
        command.add_argument("--config", default="sweep.toml", help="the sweep file, sweep.toml by default")
        if name == "run":
            command.add_argument("--out", default="runs.csv", help="where the CSV goes, runs.csv by default")
    report = commands.add_parser("report", help="print a summary of a CSV of runs")
    report.add_argument("--data", default="runs.csv", help="the CSV to read, runs.csv by default")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "expand":
        for config in expand(load(args.config).grid):
            print(config)
    elif args.command == "run":
        started = time.perf_counter()
        count = write_csv(run_all(load(args.config)), args.out)
        say(f"wrote {count} runs to {args.out} in {fmt_seconds(time.perf_counter() - started)}")
    elif args.command == "report":
        print(summary(args.data))
    return 0
