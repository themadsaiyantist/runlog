"""The Monday drift check: run what a machine can run at every lesson tag.

For each tag it checks out the reference solution in a temporary worktree and runs:

  1. the tests, which pass at every lesson tag, and on training-ground fail exactly as designed
  2. every hook the tag wires, in .claude/settings.json, the plugin's hooks.json and
     .codex/hooks.json, with a payload piped in and the exit code checked
  3. claude plugin validate, on the marketplace and the plugin, where the tag carries them
  4. the JSON and TOML files of the harness, which must parse

Nothing here calls a model or needs a credential. It needs git, uv, and claude on PATH.

    python .github/drift_check.py              every tag
    python .github/drift_check.py lesson-3.2   one tag, or several
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LESSONS = ["1.1", "1.2", "1.3", "1.4", "2.1", "2.2", "3.1", "3.2",
           "4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3"]
TAGS = ["start", *(f"lesson-{n}" for n in LESSONS), "overgrown", "training-ground"]

# The training ground starts broken on purpose: this is the last line of its pytest run.
TRAINING_GROUND_TESTS = "5 failed, 3 passed"

# From this lesson on the commit gate also catches git's global options, as in 'git -C . commit'.
GATE_CATCHES_GIT_C = [f"lesson-{n}" for n in LESSONS[LESSONS.index("5.1"):]]

# A test that always fails, added for a moment so a hook has something to refuse.
PROBE = "def test_drift_probe():\n    assert False\n"

# Where a tag may wire its hooks, and the variable that names the plugin's folder, if any.
HOOK_FILES = [
    (".claude/settings.json", None),
    ("marketplace/plugins/runlog-harness/hooks/hooks.json", "marketplace/plugins/runlog-harness"),
    (".codex/hooks.json", None),
]


def sh(*args: str, cwd: Path, **more) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **more)


def bash_payload(command: str) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}


def cases(event: str, tag: str) -> list[tuple[str, dict, bool, int]]:
    """The payloads for one event: a name, the payload, whether a test fails meanwhile, the exit code."""
    if event == "PreToolUse":
        found = [
            ("a harmless command", bash_payload("ls"), True, 0),
            ("git commit, tests green", bash_payload('git commit -m "x"'), False, 0),
            ("git commit, a test failing", bash_payload('git commit -m "x"'), True, 2),
        ]
        if tag in GATE_CATCHES_GIT_C:
            found.append(("git -C . commit, a test failing", bash_payload('git -C . commit -m "x"'), True, 2))
        return found
    if event == "Stop":
        stop = {"hook_event_name": "Stop", "stop_hook_active": False}
        return [
            ("stop, tests green", stop, False, 0),
            ("stop, a test failing", stop, True, 2),
            ("stop again after a refusal", {**stop, "stop_hook_active": True}, True, 0),
        ]
    if event == "SessionStart":
        return [("session start", {"hook_event_name": "SessionStart", "source": "startup"}, False, 0)]
    return []


def check_tests(tree: Path, tag: str) -> list[str]:
    run = sh(".venv/bin/python", "-m", "pytest", "-q", cwd=tree)
    last = (run.stdout.splitlines() or ["no output"])[-1]
    if tag == "training-ground":
        ok = TRAINING_GROUND_TESTS in last
    else:
        ok = run.returncode == 0
    return [] if ok else [f"tests: {last}"]


def check_hooks(tree: Path, tag: str) -> tuple[int, list[str]]:
    """Run every wired hook command through the shell, as the tools do, with each payload."""
    count, problems = 0, []
    probe = tree / "tests" / "test_drift_probe.py"
    for file, plugin_root in HOOK_FILES:
        if not (tree / file).exists():
            continue
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tree)}
        if plugin_root:
            env["CLAUDE_PLUGIN_ROOT"] = str(tree / plugin_root)
        for event, groups in json.loads((tree / file).read_text()).get("hooks", {}).items():
            commands = [hook["command"] for group in groups for hook in group["hooks"]]
            for command in commands:
                for name, payload, failing, expected in cases(event, tag):
                    if failing:
                        probe.write_text(PROBE)
                    run = sh("bash", "-c", command, cwd=tree, env=env,
                             input=json.dumps({**payload, "cwd": str(tree)}))
                    probe.unlink(missing_ok=True)
                    count += 1
                    if run.returncode != expected:
                        problems.append(f"{file} {event}, {name}: exit {run.returncode}, expected {expected}")
                    elif event == "SessionStart" and "Tests:" not in run.stdout:
                        problems.append(f"{file} {event}: no Tests line in its output")
    return count, problems


def check_plugin(tree: Path) -> tuple[int, list[str]]:
    if not (tree / "marketplace").exists():
        return 0, []
    if shutil.which("claude") is None:
        return 0, ["plugin: claude is not on PATH"]
    problems = []
    for target in ("marketplace", "marketplace/plugins/runlog-harness"):
        run = sh("claude", "plugin", "validate", target, cwd=tree)
        if run.returncode != 0:
            lines = (run.stdout + run.stderr).strip().splitlines()
            problems.append(f"plugin: validate {target}: {lines[-1] if lines else 'failed'}")
    return 2, problems


def check_files(tree: Path) -> tuple[int, list[str]]:
    """Every JSON and TOML file of the harness parses."""
    count, problems = 0, []
    for folder in (".claude", ".codex", "marketplace"):
        for path in sorted((tree / folder).rglob("*")) if (tree / folder).exists() else []:
            try:
                if path.suffix == ".json":
                    json.loads(path.read_text())
                elif path.suffix == ".toml":
                    tomllib.loads(path.read_text())
                else:
                    continue
                count += 1
            except ValueError as exc:
                problems.append(f"files: {path.relative_to(tree)}: {exc}")
    if (tree / ".mcp.json").exists():
        count += 1
        try:
            json.loads((tree / ".mcp.json").read_text())
        except ValueError as exc:
            problems.append(f"files: .mcp.json: {exc}")
    return count, problems


def resolve(tag: str) -> str | None:
    """The tag itself, or the branch of that name, here or on origin."""
    for ref in (tag, f"origin/{tag}"):
        if sh("git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=REPO).returncode == 0:
            return ref
    return None


def version(tool: str) -> str:
    if shutil.which(tool) is None:
        return "not installed"
    return sh(tool, "--version", cwd=REPO).stdout.strip()


def main() -> int:
    tags = sys.argv[1:] or TAGS
    print(f"Claude Code: {version('claude')}")
    print(f"Codex: {version('codex')}")
    print()
    failed = False
    with tempfile.TemporaryDirectory(prefix="drift-") as tmp:
        work = Path(tmp)
        # One virtual environment for every tag: Python 3.12 and pytest, as on the setup page.
        venv = work / "venv"
        subprocess.run(["uv", "venv", "--quiet", "--python", "3.12", str(venv)], check=True)
        subprocess.run(["uv", "pip", "install", "--quiet", "--python", str(venv / "bin" / "python"),
                        "pytest"], check=True)
        print(f"{'tag':<16} {'tests':<6} {'hooks':<6} {'plugin':<7} {'files':<6} result")
        for tag in tags:
            ref = resolve(tag)
            if ref is None:
                print(f"{tag:<16} not found")
                failed = True
                continue
            tree = work / tag
            subprocess.run(["git", "worktree", "add", "--quiet", "--detach", str(tree), ref],
                           cwd=REPO, check=True)
            try:
                (tree / ".venv").symlink_to(venv)
                problems = check_tests(tree, tag)
                tests = "ok" if not problems else "FAIL"
                hooks, found = check_hooks(tree, tag)
                problems += found
                plugin, found = check_plugin(tree)
                problems += found
                files, found = check_files(tree)
                problems += found
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=REPO, check=True)
            print(f"{tag:<16} {tests:<6} {hooks:<6} {plugin:<7} {files:<6} {'ok' if not problems else 'FAIL'}")
            for problem in problems:
                print(f"    {problem}")
            failed = failed or bool(problems)
    print()
    print("Drift found." if failed else "No drift.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
