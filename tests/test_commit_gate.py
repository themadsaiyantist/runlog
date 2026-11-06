import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parent.parent / "tools" / "hooks" / "commit_gate.py"
spec = importlib.util.spec_from_file_location("commit_gate", GATE)
commit_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(commit_gate)


@pytest.mark.parametrize("command", [
    "git commit -m x",
    "git -C . commit -m x",
    "git -C /some/path commit",
    "git -c user.name=x commit -m x",
    "git --git-dir=.git --no-pager commit",
    "/usr/bin/git commit",
    "cd sub && git -C .. commit -m 'x'",
    "git add . ; git commit",
    "git commit -m 'unbalanced",
])
def test_these_are_commits(command):
    assert commit_gate.is_git_commit(command)


@pytest.mark.parametrize("command", [
    "git status",
    "git log --grep commit",
    "git -C . log",
    "grep commit file.txt",
])
def test_these_are_not(command):
    assert not commit_gate.is_git_commit(command)


def fake_project(tmp_path, exit_code):
    """A project whose .venv/bin/python exits with exit_code, like a test run that passes or fails."""
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text(f"#!/bin/sh\necho 'FAILED tests/x.py::t'\necho '1 failed'\nexit {exit_code}\n")
    python.chmod(0o755)
    return tmp_path


def run_gate(stdin, project):
    return subprocess.run([sys.executable, str(GATE)], input=stdin, capture_output=True, text=True,
                          env={"CLAUDE_PROJECT_DIR": str(project), "PATH": "/usr/bin:/bin"})


def payload(command):
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def test_a_failing_test_refuses_git_dash_c_commit(tmp_path):
    result = run_gate(payload("git -C . commit -m x"), fake_project(tmp_path, 1))
    assert result.returncode == 2
    assert "FAILED tests/x.py::t" in result.stderr


def test_passing_tests_let_the_commit_through(tmp_path):
    assert run_gate(payload("git -C . commit -m x"), fake_project(tmp_path, 0)).returncode == 0


def test_a_command_that_is_not_a_commit_runs_no_tests(tmp_path):
    assert run_gate(payload("git status"), tmp_path).returncode == 0   # no python there to run


def test_a_crash_on_bad_input_refuses_the_commit(tmp_path):
    result = run_gate("not json", fake_project(tmp_path, 0))
    assert result.returncode == 2
    assert "crashed" in result.stderr


def test_a_crash_running_the_tests_refuses_the_commit(tmp_path):
    result = run_gate(payload("git commit -m x"), tmp_path)   # no .venv: the gate cannot run the tests
    assert result.returncode == 2
    assert "crashed" in result.stderr


def test_failing_tests_with_no_output_still_refuse(tmp_path):
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text("#!/bin/sh\nexit 1\n")
    python.chmod(0o755)
    assert run_gate(payload("git commit"), tmp_path).returncode == 2


def test_settings_send_every_bash_command_to_the_gate():
    settings = json.loads((GATE.parent.parent.parent / ".claude" / "settings.json").read_text())
    hooks = [h for entry in settings["hooks"]["PreToolUse"] for h in entry["hooks"]
             if "commit_gate.py" in h["command"]]
    assert hooks and all("if" not in h for h in hooks)
