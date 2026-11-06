"""The report over a runs.csv: how many runs, the best one, the mean accuracy of every model."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def read(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def best(rows: list[dict]) -> dict:
    return max(rows, key=lambda row: float(row["val_accuracy"]))


def summary(path: str | Path) -> str:
    raise NotImplementedError("TODO: the report, see the README for what it prints")
    rows = read(path)
    if not rows:
        return "runs: 0"
    top = best(rows)
    totals: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        totals[row["model"]].append(float(row["val_accuracy"]))
    lines = [
        f"runs: {len(rows)}",
        f"best: {top['run_id']} {top['model']} lr={top['learning_rate']} epochs={top['epochs']} "
        f"acc={float(top['val_accuracy']):.3f} loss={float(top['val_loss']):.3f}",
        "mean accuracy by model:",
    ]
    for model, values in sorted(totals.items()):
        lines.append(f"  {model:<12} {sum(values) / len(values):.3f}")
    return "\n".join(lines)
