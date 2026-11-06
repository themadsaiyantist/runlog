"""Print the run report with every number filled in. The agent writes the two TODO lines."""

import datetime
import subprocess
import sys
from pathlib import Path

PYTHON = ".venv/bin/python"


def run(*args: str) -> str:
    """Run a command with the project's Python, and stop the report if it fails."""
    result = subprocess.run([PYTHON, *args], capture_output=True, text=True)
    if result.returncode != 0 and args[1] == "runlog":
        sys.exit(result.stderr.strip())
    return result.stdout.strip()


since = ["--since", sys.argv[1]] if len(sys.argv) > 1 else []
today = datetime.date.today().isoformat()
title = f"# Run report, {today}" + (f", runs since {sys.argv[1]}" if since else "")

count, best, *table = run("-m", "runlog", "report", "--format", "md", *since).splitlines()[1:]
top = run("-m", "runlog", "best", "--top", "3", *since).splitlines()
tests = run("-m", "pytest", "-q").splitlines()[-1]
log = Path("logs/train.log")
errors = sum(line.split()[2] == "ERROR" for line in log.open()) if log.exists() else "no log"

print(title, "", "**Summary:** TODO", "", "## Numbers", "", f"- {count}", f"- {best}", "", *table, "", sep="\n")
print("## Top 3", "", *[f"- `{line}`" for line in top], "", sep="\n")
print("## Health", "", f"- Tests: {tests}", f"- ERROR lines in logs/train.log: {errors}", "", sep="\n")
print("## Next", "", "TODO", sep="\n")
