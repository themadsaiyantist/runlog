"""Writing rows as the runs.csv that runlog reads."""

from __future__ import annotations

import csv
from pathlib import Path

COLUMNS = ["run_id", "date", "model", "learning_rate", "epochs", "val_acc", "val_loss"]


def write_csv(rows: list[dict], path: str | Path) -> int:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in COLUMNS})
    return len(rows)
