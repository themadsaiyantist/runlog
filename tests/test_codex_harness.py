"""Exercise the configured hooks with Codex payloads, without running nested pytest."""

import datetime
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = json.loads((ROOT / ".codex" / "hooks.json").read_text())["hooks"]


def make_project(tmp_path, exit_code=0):
    project = tmp_path / "project with spaces"
    python = project / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    summary = "1 failed" if exit_code else "3 passed"
    python.write_text(
        '#!/bin/sh\n'
        'if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then\n'
        '  pwd > pytest-cwd\n'
        + ('  echo "FAILED tests/example.py::test_example"\n' if exit_code else '')
        + f'  echo "{summary}"\n  exit {exit_code}\nfi\n'
        + f'exec {shlex.quote(sys.executable)} "$@"\n'
    )
    python.chmod(0o755)
    shutil.copytree(ROOT / "tools" / "hooks", project / "tools" / "hooks",
                    ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(["git", "init", "-q", "--initial-branch=harness-test", str(project)],
                   check=True, capture_output=True)
    (project / "nested").mkdir()
    return project


def run_hook(project, event, **extra):
    # Codex canonicalizes exec_command to Bash and supplies command, not cmd.
    payload = {
        "session_id": "test-session",
        "transcript_path": None,
        "cwd": str(project / "nested"),
        "hook_event_name": event,
        "permission_mode": "default",
        **extra,
    }
    match_value = payload.get("tool_name", payload.get("source", ""))
    handlers = [handler for entry in HOOKS[event]
                if re.search(entry.get("matcher", ""), match_value)
                for handler in entry["hooks"]]
    assert len(handlers) == 1
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    return subprocess.run(["bash", "-c", handlers[0]["command"]],
                          cwd=project / "nested", env=env,
                          input=json.dumps(payload), capture_output=True,
                          text=True, timeout=10)


@pytest.mark.parametrize("exit_code", [0, 1])
def test_codex_commit_gate_blocks_only_failing_tests(tmp_path, exit_code):
    project = make_project(tmp_path, exit_code)
    result = run_hook(project, "PreToolUse", turn_id="turn-1", tool_name="Bash",
                      tool_use_id="call-1",
                      tool_input={"command": "git -C . commit -m example"})
    assert result.returncode == (2 if exit_code else 0)
    assert (project / "pytest-cwd").read_text().strip() == str(project)
    if exit_code:
        assert "FAILED tests/example.py::test_example" in result.stderr


def test_codex_non_commit_does_not_run_tests(tmp_path):
    project = make_project(tmp_path, 1)
    result = run_hook(project, "PreToolUse", tool_name="Bash",
                      tool_input={"command": "git status"})
    assert result.returncode == 0
    assert not (project / "pytest-cwd").exists()


@pytest.mark.parametrize("source", ["startup", "clear", "compact"])
def test_codex_session_context_from_a_subdirectory(tmp_path, source):
    project = make_project(tmp_path, 1)
    result = run_hook(project, "SessionStart", source=source)
    assert result.returncode == 0
    assert "Branch: harness-test" in result.stdout
    assert "Tests: 1 failed" in result.stdout
    assert "FAILED tests/example.py::test_example" in result.stdout
    assert (project / "pytest-cwd").read_text().strip() == str(project)


@pytest.mark.parametrize("exit_code", [0, 1])
def test_codex_stop_checks_tests(tmp_path, exit_code):
    project = make_project(tmp_path, exit_code)
    result = run_hook(project, "Stop", turn_id="turn-1", stop_hook_active=False,
                      last_assistant_message="Finished.")
    assert result.returncode == (2 if exit_code else 0)
    assert (project / "pytest-cwd").read_text().strip() == str(project)
    assert not result.stdout
    if exit_code:
        assert "Fix them before you stop" in result.stderr


def test_codex_stop_does_not_loop_after_continuation(tmp_path):
    project = make_project(tmp_path, 1)
    result = run_hook(project, "Stop", stop_hook_active=True)
    assert result.returncode == 0
    assert not result.stdout
    assert not (project / "pytest-cwd").exists()


@pytest.mark.parametrize("cutoff, count", [(None, 4), ("2026-09-03", 2)])
def test_codex_report_renderer(tmp_path, runs_csv, cutoff, count):
    project = make_project(tmp_path)
    shutil.copytree(ROOT / "runlog", project / "runlog",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(runs_csv, project / "runs.csv")
    skill = project / ".agents" / "skills" / "report"
    shutil.copytree(ROOT / ".agents" / "skills" / "report", skill)
    args = [".venv/bin/python", ".agents/skills/report/render.py"]
    result = subprocess.run(args + ([cutoff] if cutoff else []), cwd=project,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith(f"# Run report, {datetime.date.today().isoformat()}")
    assert f"- Runs: {count}\n" in result.stdout
    assert "bert-base | 0.904" in result.stdout
    assert "- Tests: 3 passed" in result.stdout
    assert "**Summary:** TODO" in result.stdout
    assert result.stdout.endswith("## Next\n\nTODO\n")
    if cutoff:
        assert f"runs since {cutoff}" in result.stdout
        assert "resnet18" not in result.stdout
