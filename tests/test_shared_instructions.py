"""Keep both tools pointed at the same project instructions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_claude_imports_shared_instructions():
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert claude.strip() == "@AGENTS.md"
    shared = ROOT / claude.strip().removeprefix("@")
    assert shared.is_file()
    assert "## Conventions" in shared.read_text(encoding="utf-8")


def test_conventions_link_to_shared_instructions_without_copying_rules():
    conventions = (ROOT / "docs" / "conventions.md").read_text(encoding="utf-8")
    assert "[AGENTS.md](../AGENTS.md#conventions)" in conventions
    assert not any(line.startswith("- ") for line in conventions.splitlines())
