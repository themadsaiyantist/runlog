"""Stop hook: the agent does not stop while a test fails."""

import json
import os
import subprocess
import sys

payload = json.load(sys.stdin)
if payload.get("stop_hook_active"):
    sys.exit(0)

project = os.environ.get("CLAUDE_PROJECT_DIR", ".")
tests = subprocess.run([f"{project}/.venv/bin/python", "-m", "pytest", "-q"],
                       cwd=project, capture_output=True, text=True)
if tests.returncode != 0:
    lines = tests.stdout.splitlines()
    failed = [line for line in lines if line.startswith("FAILED")]
    print("The tests fail. Fix them before you stop.", *failed, lines[-1], sep="\n",
          file=sys.stderr)
    sys.exit(2)
