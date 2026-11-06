"""The old best-run picker. It compares the accuracy column as text, so .9 loses to 0.89 (0.9 does win)."""

import csv


def best(path):
    with open(path) as f:
        rows = list(csv.reader(f))[1:]
    return max(rows, key=lambda row: row[5])
