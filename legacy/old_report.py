"""The old report. It prints six columns by position and breaks the day a column is added."""

import csv


def report(path):
    with open(path) as f:
        rows = list(csv.reader(f))[1:]
    print(f"{len(rows)} runs")
    for row in rows:
        print(f"{row[0]:<6} {row[1]:<12} {row[2]:<8} {row[3]:<4} {row[4]:<6} {row[5]:<6}")
