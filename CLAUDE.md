# runlog

A small command-line tool over runs.csv, a log of training runs. Python 3.12, with the virtual environment in .venv.

## Commands

- Run the tests: `.venv/bin/python -m pytest`
- Run the tool: `.venv/bin/python -m runlog best`, `report` or `show RUN_ID`

## Conventions

@docs/conventions.md

## Large files

- Before you open a large file, check its size with `wc -l`. Search it with `grep` instead of reading it, and read only the lines you need.
