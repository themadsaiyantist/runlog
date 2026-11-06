"""Summaries over a list of runs."""

from __future__ import annotations

import math
from collections import defaultdict

from .data import Run


def _rank_key(run: Run) -> tuple[float, float, str]:
    """Higher accuracy first, then lower loss (a NaN loss last), then the earlier date."""
    loss = math.inf if math.isnan(run.val_loss) else run.val_loss
    return (-run.val_accuracy, loss, run.date)


def _rankable(runs: list[Run]) -> list[Run]:
    """The runs with a number for accuracy, in file order: a NaN accuracy is never ranked.

    Raises ValueError when none are left.
    """
    if not runs:
        raise ValueError("no runs to choose from")
    kept = [run for run in runs if not math.isnan(run.val_accuracy)]
    if not kept:
        raise ValueError("no runs with a validation accuracy to choose from, every one is NaN")
    return kept


def best_run(runs: list[Run]) -> Run:
    """The run with the highest validation accuracy.

    On a tie the lower validation loss wins, then the earlier date, then the first one in file order.
    A run whose accuracy is NaN is never chosen.
    """
    return min(_rankable(runs), key=_rank_key)


def top_runs(runs: list[Run], count: int) -> list[Run]:
    """The count runs with the highest validation accuracy, highest first.

    Ties rank the same way as in best_run: lower loss, then earlier date, then file order.
    Runs whose accuracy is NaN are left out.
    """
    if count < 1:
        raise ValueError("--top needs a count of at least 1")
    return sorted(_rankable(runs), key=_rank_key)[:count]


def mean_accuracy_by_model(runs: list[Run]) -> dict[str, float]:
    """The mean validation accuracy of every model, by model name."""
    totals: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        totals[run.model].append(run.val_accuracy)
    return {model: sum(values) / len(values) for model, values in sorted(totals.items())}


def runs_by_model(runs: list[Run]) -> dict[str, int]:
    """The number of runs of every model, by model name, sorted by name."""
    counts: dict[str, int] = defaultdict(int)
    for run in runs:
        counts[run.model] += 1
    return dict(sorted(counts.items()))


def format_models(runs: list[Run]) -> str:
    """One line per model, its name and its number of runs, sorted by name."""
    return "\n".join(f"{model:<12} {count}" for model, count in runs_by_model(runs).items())


def format_run(run: Run) -> str:
    """One run on one line."""
    return (
        f"{run.run_id}  {run.model:<12} lr={run.learning_rate:<8g} "
        f"epochs={run.epochs:<3} acc={run.val_accuracy:.3f}  loss={run.val_loss:.3f}"
    )


def format_row(row: dict[str, str]) -> str:
    """One run in full: every column on its own line as 'name: value', in the order given."""
    return "\n".join(f"{name}: {value}" for name, value in row.items())


def summary(runs: list[Run]) -> str:
    """The report: the count, the best run, and the mean accuracy of every model."""
    lines = [f"runs: {len(runs)}", f"best: {format_run(best_run(runs))}", "mean accuracy by model:"]
    for model, accuracy in mean_accuracy_by_model(runs).items():
        lines.append(f"  {model:<12} {accuracy:.3f}")
    return "\n".join(lines)


def markdown_summary(runs: list[Run]) -> str:
    """The same report as Markdown: a heading, the count, the best run, and a table by model."""
    lines = [
        "# runlog report",
        f"Runs: {len(runs)}",
        f"Best: {format_run(best_run(runs))}",
        "| Model | Mean accuracy |",
        "| --- | --- |",
    ]
    for model, accuracy in mean_accuracy_by_model(runs).items():
        lines.append(f"| {model} | {accuracy:.3f} |")
    return "\n".join(lines)
