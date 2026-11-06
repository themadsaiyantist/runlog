"""Loading runs from a CSV file."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

COLUMNS = ["run_id", "date", "model", "learning_rate", "epochs", "val_accuracy", "val_loss"]


@dataclass(frozen=True)
class Run:
    run_id: str
    date: str
    model: str
    learning_rate: float
    epochs: int
    val_accuracy: float
    val_loss: float


def load_runs(path: str | Path) -> list[Run]:
    """Every run in the CSV at 'path', in file order.

    Raises ValueError when a column is missing, or when a row has a missing, empty or unreadable field.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        return [_parse_row(row, f"{path}, line {reader.line_num}") for row in reader]


def _parse_row(row: dict[str, str | None], where: str) -> Run:
    """One row as a Run. Raises ValueError naming 'where' when a field is missing, empty or unreadable."""
    empty = [c for c in COLUMNS if row.get(c) is None or not row[c].strip()]
    if empty:
        raise ValueError(f"{where}: missing value for {empty}")
    try:
        return Run(
            run_id=row["run_id"],
            date=row["date"],
            model=row["model"],
            learning_rate=float(row["learning_rate"]),
            epochs=int(row["epochs"]),
            val_accuracy=float(row["val_accuracy"]),
            val_loss=float(row["val_loss"]),
        )
    except ValueError as exc:
        raise ValueError(f"{where}: {exc}") from None
