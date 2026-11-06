"""The loader before the rewrite. It trusts the column order and never reads the header."""

import csv


def load(path):
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            rows.append((row[0], row[2], float(row[3]), int(row[4]), float(row[5]), float(row[6])))
    return rows
