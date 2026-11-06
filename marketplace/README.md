# runlog-plugins

A Claude Code marketplace with one plugin, `runlog-harness`, the harness built in the course Coding Agents.

## What it installs

- `report`, a skill that writes a run report of one fixed shape into `reports/`
- `reviewer` and `test-writer`, two agents: one reviews a change without editing, one writes tests in its own worktree
- three hooks: no commit while a test fails, the branch and the tests at session start, the tests before the agent stops
- `review-runlog`, a workflow that reviews a folder on three dimensions and verifies every finding
- `fetch`, an MCP server run through `uvx`

The hooks run the project's tests with `.venv/bin/python -m pytest`, so they expect a Python project with its virtual environment in `.venv`.

## Install

```bash
claude plugin marketplace add <owner>/runlog-plugins
claude plugin install runlog-harness@runlog-plugins
```
