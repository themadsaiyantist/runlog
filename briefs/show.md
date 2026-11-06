# runlog show RUN_ID

Goal: a new command, `runlog show RUN_ID`, prints one run in full: every column of runs.csv on its own line, as `name: value`, in the order the CSV has them.

Files: the command goes in runlog/cli.py, beside best and report. The formatting goes in runlog/report.py, beside format_run.

Constraints: the standard library only. No change to best, report, the CSV, or any existing test. It honours --data like the other commands. An id that is not in the file ends the command with a `runlog: ` message on stderr and exit code 1.

Done: new tests in tests/test_show.py cover a run that exists and an id that does not. The whole suite passes with .venv/bin/python -m pytest, and nothing is committed.
