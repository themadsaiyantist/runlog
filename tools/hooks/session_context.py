"""SessionStart hook: tell the agent the branch and the state of the tests."""

import os
import subprocess

project = os.environ.get("CLAUDE_PROJECT_DIR", ".")


def run(*args: str) -> list[str]:
    return subprocess.run(args, cwd=project, capture_output=True, text=True).stdout.splitlines()


branch = run("git", "branch", "--show-current")
tests = run(f"{project}/.venv/bin/python", "-m", "pytest", "-q")
print(f"Branch: {branch[0] if branch else 'none'}")
print(f"Tests: {tests[-1] if tests else 'did not run'}")
for line in tests:
    if line.startswith("FAILED"):
        print(line)
