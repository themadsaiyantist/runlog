# runlog

A small command-line tool over runs.csv, a log of training runs. Python 3.12, with the virtual environment in .venv.

## Commands

- Run the tests: `.venv/bin/python -m pytest`
- Run the tests quietly: `.venv/bin/python -m pytest -q`
- Run one test file: `.venv/bin/python -m pytest tests/test_best.py`
- Run the tool: `.venv/bin/python -m runlog best`, `report` or `show RUN_ID`
- `.venv/bin/python -m runlog best --top 5` prints the five best runs.
- `.venv/bin/python -m runlog best --since 2026-08-15` keeps runs from that date on.
- `.venv/bin/python -m runlog best --model bert-base` keeps one model.
- `.venv/bin/python -m runlog best --min-epochs 10` keeps runs with at least 10 epochs.
- `.venv/bin/python -m runlog report --format md` prints the report as Markdown.
- `.venv/bin/python -m runlog models` lists every model and its number of runs.
- `.venv/bin/python scripts/make_log.py` writes logs/train.log.
- `.venv/bin/python scripts/import_raw.py` rebuilds runs.csv from data/raw/.

## Conventions

@docs/conventions.md

- Standard library only: csv, argparse, dataclasses. No pandas, no new dependencies.
- Every change comes with a test in tests/, and the whole suite passes before you report.
- Model names are lowercase, as the exports write them. Lowercase any model name a user types before you compare it.
- Use the standard library. Do not add pandas, numpy or click.
- Write a test for every change.
- Lowercase model names.

## Large files

- Before you open a large file, check its size with `wc -l`. Search it with `grep` instead of reading it, and read only the lines you need.
- logs/train.log is 5,000 lines. Never read it whole.

## Architecture

- runlog/__init__.py is empty.
- runlog/__main__.py calls cli.main and exits with its return code.
- runlog/cli.py holds the argument parser and main.
- build_parser in cli.py defines the subcommands best, report, show and models.
- main in cli.py loads the runs, applies --since, then --model, then --min-epochs, then calls the command.
- parse_since in cli.py checks that a date is written YYYY-MM-DD.
- runs_since in cli.py keeps the runs from a date on.
- runs_of_model in cli.py keeps the runs of one model, lowercased.
- runs_with_min_epochs in cli.py keeps the runs with at least N epochs.
- find_row in cli.py finds one row by its id for show.
- runlog/data.py holds the Run dataclass and load_runs.
- load_runs reads the CSV with csv.DictReader and checks the columns.
- COLUMNS in data.py lists the seven columns in order.
- runlog/report.py holds best_run, top_runs, mean_accuracy_by_model, summary and markdown_summary.
- best_run ranks by accuracy, then lower loss, then the earlier date, then file order.
- top_runs uses the same ranking as best_run.
- format_run prints one run on one line.
- format_row prints one run in full for show.
- runs_by_model and format_models are in report.py, for the models command.
- scripts/import_raw.py reads data/raw/*.csv and writes runs.csv.
- scripts/make_log.py writes a fake training log from a fixed seed.
- legacy/ holds the old modules, old_best.py, old_loader.py and old_report.py.
- tests/conftest.py has the runs_csv fixture with four runs.
- tools/hooks/ holds the three hooks.

## The data

- runs.csv has one row per run.
- run_id is r001, r002 and so on.
- date is written YYYY-MM-DD.
- model is the model's name, lowercase.
- learning_rate is a float, like 0.001 or 2e-05.
- epochs is an int.
- val_accuracy is a float between 0 and 1.
- val_loss is a float.
- There are 30 runs in runs.csv.
- The models are bert-base, distilbert, resnet18, resnet50 and xgb-tabular.
- The raw exports in data/raw/ have a host column that runs.csv does not have.
- The training machine gpu-01 was renamed gpu-a. The raw exports still say gpu-01.

## History

- In July runlog used pandas. We removed it in August because the course says standard library only.
- The old loader in legacy/ read columns by position. The rewrite reads them by name.
- notes/old_runs.csv was removed in lesson 1.2.
- The tie rule was added in lesson 1.3: lower loss, then the earlier date, then file order.
- show was added in lesson 1.4.
- --model was added in lesson 2.1, --min-epochs in lesson 3.2, models in lesson 4.3.
- We tried a --format json for report once and dropped it.

## How to write the run report

When I ask for the run report, do it like this every time:

1. Run `.venv/bin/python -m runlog report --format md`.
2. Run `.venv/bin/python -m runlog best --top 3`.
3. Run `.venv/bin/python -m pytest -q` and keep the last line.
4. Count the ERROR lines in logs/train.log with grep -c.
5. Write reports/YYYY-MM-DD.md with a title, a Summary line, Numbers, Top 3, Health and Next.
6. The Summary is one sentence: the number of runs, the best run, and what stands out.
7. Next is one suggestion for the next run, from the numbers only.
8. Do not commit the report.
9. Reply with the path and the summary line.

## How to review a change

When I ask for a review:

1. Read the diff with git diff or git show.
2. Read the code around the change.
3. Check it against docs/conventions.md.
4. Run the tests.
5. Report at most five findings, most important first, each with the file and line.
6. Do not change any file during a review.
7. If there is nothing to report, say so in one line.

## Rules that must never be broken

- NEVER edit anything in data/raw/. Those are the exports as the machine wrote them.
- NEVER commit while a test fails. This includes commits written as `git -C . commit`.
- NEVER push without asking me first.
- NEVER delete a test to make the suite pass.
- NEVER install a package.
- Never run `rm -rf` anywhere.

## My preferences

- Keep answers short. Lead with the result.
- Call me goku.
- I like tables for comparisons.
- Do not use emojis.
- Explain a command before you run something that deletes files.
- End every report with the list of files you changed.
- I work on WSL, so paths look like /home/goku.

## Local notes

- When you run the tests, add -q so the output stays short.
- My venv is in .venv. If it is missing, make it with uv venv --python 3.12 .venv.
- I keep a scratch file at notes/scratch.md that is not committed.

## Style

- Write docstrings in full sentences.
- Keep functions short.
- Use type hints on every function.
- Use f-strings, not format or %.
- Name tests test_<what it checks>.
- Keep error messages starting with runlog: and exit 1.
- Print to stdout, errors to stderr.
- One command per function in cli.py.
- Keep line length under 120 characters.
- Prefer pathlib over os.path.
- Sort imports: standard library, then local.
- Do not leave print statements for debugging.
- Do not catch bare Exception.
- Comments explain why, not what.

## Troubleshooting

- If `python -m runlog` says No module named runlog, you are not in the project's folder.
- If pytest is missing, run uv pip install --python .venv/bin/python pytest.
- If import fails with No module named pandas, run pip install pandas.
- If report crashes with a traceback on an empty log, that was fixed in lesson 1.4.
- If the hooks fail with No such file, the .venv is missing.
- If a test fails only on your machine, delete .pytest_cache and run again.
- If runs.csv looks wrong, rebuild it with scripts/import_raw.py, never by hand.
- If best prints the wrong run, check the tie rule.
- If a date is rejected, it must be YYYY-MM-DD.
- If the session start note says Tests: did not run, the .venv is missing.
- If a worktree has no .venv, make one there too.
- If the fetch server does not start, check that uv is installed.
- If the GitHub server fails, export GITHUB_PAT before starting claude.

## Known bugs

- A row with a missing field crashes best and report with a TypeError instead of a runlog: error.
- A NaN accuracy can be reported as the best run.
- The commit gate lets a commit through when pytest prints nothing.
- The commit gate misses `git -C . commit`.
- legacy/old_best.py has a docstring that says 0.9 loses to 0.89, which is wrong.

## Release checklist

When I say release:

1. Run the whole suite.
2. Check git status is clean.
3. Update the version in pyproject.toml.
4. Write the changes in the README.
5. Commit with the message release X.Y.Z.
6. Tag it vX.Y.Z.
7. Ask me before you push the tag.

## Old notes

- TODO: add --format json to report? (no, dropped)
- TODO: move legacy/ out once nothing reads it.
- The report skill is in .claude/skills/report.
- The reviewer agent is in .claude/agents/reviewer.md.
- The test-writer agent is in .claude/agents/test-writer.md.
- The review workflow is in .claude/workflows/review-runlog.js.
- The fetch server is in .mcp.json.
- The plugin is in marketplace/.
- Remember: standard library only.
- Remember: lowercase model names.
- Remember: a test with every change.
- Remember: never edit data/raw.
- Remember: search large files, do not read them.
- Remember: short answers.
- The tests take under a second.
- There are 64 tests.
- runs.csv has 30 rows.
- The best run is r010, bert-base, 0.932.
- Python is 3.12.
- The default branch is main.
- The course is Coding Agents.
- Ask before big changes.
- Be careful with the hooks.
- Read the README first.
