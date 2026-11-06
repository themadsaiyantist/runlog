# --since DATE

Goal: a --since DATE option on `best` and `report` keeps only the runs from DATE on, DATE included, before anything is ranked or counted. Without --since, both commands print what they print now.

Files: the option goes in runlog/cli.py, beside --top and --format. A run's date is the date column runlog/data.py loads from runs.csv.

Constraints: the standard library only. No change to the CSV, to the printed formats, or to any existing test. A DATE the option cannot read, and a DATE after the last run, both end the command with a `runlog: ` message on stderr and exit code 1, the way a missing file does.

Ask first: before you choose the date format --since accepts, ask me, with the formats you would consider. Write no code until I answer.

Done: new tests in tests/test_since.py cover a DATE that keeps some runs, a DATE after the last run, and a DATE the option cannot read. The whole suite passes with .venv/bin/python -m pytest, and nothing is committed.
