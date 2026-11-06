"""PreToolUse hook: refuse a git commit while a test fails."""

import json
import os
import subprocess
import sys

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")
if payload.get("tool_name") != "Bash" or "git commit" not in command:
    sys.exit(0)

project = os.environ.get("CLAUDE_PROJECT_DIR", ".")
tests = subprocess.run([f"{project}/.venv/bin/python", "-m", "pytest", "-q"],
                       cwd=project, capture_output=True, text=True)
if tests.returncode != 0:
    lines = tests.stdout.splitlines()
    failed = [line for line in lines if line.startswith("FAILED")]
    print("A test fails, so this commit is refused. Make the tests pass, then commit again.",
          *failed, lines[-1], sep="\n", file=sys.stderr)
    sys.exit(2)
