# runlog

A small command-line tool over runs.csv, a log of training runs. Python 3.12,
with the virtual environment in .venv. Run commands from the repository root.

## Commands

- Run the tests: `.venv/bin/python -m pytest`
- Run the tool: `.venv/bin/python -m runlog best`, `report` or `show RUN_ID`
- Write a run report with the `report` skill in `.agents/skills/report/SKILL.md`.

## Conventions

- Standard library only: csv, argparse, dataclasses. No pandas, no new dependencies.
- Every change comes with a test in tests/, and the whole suite passes before you report.
- Model names are lowercase, as the exports write them. Lowercase any model name a user types before you compare it.

## Large files

- Before you open a large file, check its size with `wc -l`. Search it with `rg`
  instead of reading it, and read only the lines you need.

## Repository safeguards

- Keep `data/raw/` unchanged, matching the Claude harness's edit restriction.
- Ask before `git push`, matching the Claude harness's permission rule.
- These are agent instructions; Codex permissions and sandbox settings are separate.

See `docs/codex-harness.md` for hook setup and the remaining migration gaps.
