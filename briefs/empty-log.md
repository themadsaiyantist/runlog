# report on an empty log

Goal: runlog report on a log that has a header and no runs prints a `runlog: ` message on stderr and exits 1, in both formats, the way runlog best already does. Today it crashes with a Python traceback.

Files: runlog/cli.py, where main runs report. tests/test_empty.py describes the fix.

Constraints: tests/test_empty.py and every other test pass unchanged. No change to what report prints for a log that has runs.

Done: the whole suite passes with .venv/bin/python -m pytest, and nothing is committed.
