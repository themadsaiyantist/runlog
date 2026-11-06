"""Summaries over a list of runs."""

from __future__ import annotations

from collections import defaultdict

from .data import Run


def best_run(runs: list[Run]) -> Run:
    """The run with the highest validation accuracy. The first one in file order wins a tie."""
    if not runs:
        raise ValueError("no runs to choose from")
    return max(runs, key=lambda run: run.val_accuracy)


def mean_accuracy_by_model(runs: list[Run]) -> dict[str, float]:
    """The mean validation accuracy of every model, by model name."""
    totals: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        totals[run.model].append(run.val_accuracy)
    return {model: sum(values) / len(values) for model, values in sorted(totals.items())}


def format_run(run: Run) -> str:
    """One run on one line."""
    return (
        f"{run.run_id}  {run.model:<12} lr={run.learning_rate:<8g} "
        f"epochs={run.epochs:<3} acc={run.val_accuracy:.3f}  loss={run.val_loss:.3f}"
    )


def summary(runs: list[Run]) -> str:
    """The report: the count, the best run, and the mean accuracy of every model."""
    lines = [f"runs: {len(runs)}", f"best: {format_run(best_run(runs))}", "mean accuracy by model:"]
    for model, accuracy in mean_accuracy_by_model(runs).items():
        lines.append(f"  {model:<12} {accuracy:.3f}")
    return "\n".join(lines)
