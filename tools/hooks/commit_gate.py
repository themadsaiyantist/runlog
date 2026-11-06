"""PreToolUse hook: refuse a git commit while a test fails.

Exit 0 lets the command run; exit 2 refuses it. Any crash in the gate itself also exits 2,
since a gate that cannot check the tests must not let a commit through.
"""

import json
import os
import re
import shlex
import subprocess
import sys

# git's global options that take their value as the next word, as in 'git -C . commit'.
OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix",
                      "--config-env", "--exec-path", "--list-cmds", "--attr-source"}


def is_git_commit(command: str) -> bool:
    """Whether the shell command runs 'git commit', with or without git's global options before it."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        # Unbalanced quotes: when in doubt, gate it.
        return re.search(r"\bgit\b.*\bcommit\b", command, re.DOTALL) is not None
    for i, word in enumerate(words):
        if os.path.basename(word) != "git":
            continue
        j = i + 1
        while j < len(words) and words[j].startswith("-"):
            j += 2 if words[j] in OPTIONS_WITH_VALUE else 1
        if j < len(words) and words[j] == "commit":
            return True
    return False


def gate(payload: dict, project: str) -> int:
    """The exit code for this hook payload: 0 to let the command run, 2 to refuse it."""
    command = payload.get("tool_input", {}).get("command", "")
    if payload.get("tool_name") != "Bash" or not is_git_commit(command):
        return 0
    tests = subprocess.run([f"{project}/.venv/bin/python", "-m", "pytest", "-q"],
                           cwd=project, capture_output=True, text=True)
    if tests.returncode != 0:
        lines = tests.stdout.splitlines()
        failed = [line for line in lines if line.startswith("FAILED")]
        last = lines[-1:] or tests.stderr.splitlines()[-1:]
        print("A test fails, so this commit is refused. Make the tests pass, then commit again.",
              *failed, *last, sep="\n", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    try:
        return gate(json.load(sys.stdin), os.environ.get("CLAUDE_PROJECT_DIR", "."))
    except Exception as exc:
        print(f"The commit gate crashed, so this commit is refused: {exc!r}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
