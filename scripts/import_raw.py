"""Rebuild runs.csv from the raw exports in data/raw/, so the committed table is never edited by hand.

Each export is a CSV the training machine wrote, with its own column names. This script keeps the
columns runlog reads, renames them, and writes every run in file order, one export after another.
"""

from __future__ import annotations

import csv
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("runs.csv")
FIELDS = ["run_id", "date", "model", "learning_rate", "epochs", "val_accuracy", "val_loss"]


def rebuild(raw: Path = RAW, out: Path = OUT) -> int:
    rows = []
    for path in sorted(raw.glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(
                    {
                        "run_id": row["run_id"],
                        "date": row["started"][:10],
                        "model": row["model"],
                        "learning_rate": row["lr"],
                        "epochs": row["epochs"],
                        "val_accuracy": row["val_acc"],
                        "val_loss": row["val_loss"],
                    }
                )
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    print(f"wrote {rebuild()} runs to {OUT}")
