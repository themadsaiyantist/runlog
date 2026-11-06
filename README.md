# runlog

A small command-line tool over `runs.csv`, a log of training runs with one row per run: its id, the date, the model, the learning rate, the epochs, and the validation accuracy and loss. It reads the file with the standard library and prints what you ask for.

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pytest
.venv/bin/python -m runlog best
.venv/bin/python -m runlog report
.venv/bin/python -m runlog best --since 2026-08-15
.venv/bin/python -m runlog report --since 2026-08-15
.venv/bin/python -m runlog show r001
.venv/bin/python -m runlog best --top 5
.venv/bin/python -m runlog report --format md
.venv/bin/python -m runlog best --model bert-base
.venv/bin/python -m pytest
```

`best` prints the run with the highest validation accuracy. `report` prints how many runs there are, the best one, and the mean accuracy of every model. Both take `--data PATH` to read another file instead of `runs.csv`, and `--since DATE`, written YYYY-MM-DD, to keep only the runs from DATE on, DATE included. A DATE in another form, or one after the last run, ends the command with an error.

`show RUN_ID` prints one run in full, one column per line, as the CSV writes it, and takes `--data PATH` too. An id that is not in the file ends the command with an error.

- `best --top N` prints the N best runs, highest first, instead of only the best one.
- `report --format md` prints the report as Markdown instead of text.
- `--model NAME`, on `best` and `report`, keeps only the runs of that model. The name is lowercased first, so `ResNet18` finds `resnet18`. A model with no runs left ends the command with an error.

## How the project works

- `runs.csv` is built from the exports in `data/raw/` by `scripts/import_raw.py`. A change to the data goes into a raw export and the script, never into `runs.csv` by hand.
- `data/raw/` holds the exports exactly as the training machine wrote them, and nothing edits them.
- The standard library only: `csv`, `argparse`, `dataclasses`. No pandas.
- Every change comes with a test in `tests/`, and `pytest` passes before a commit.
- Model names are lowercase, as the exports write them.
- `logs/` is gitignored, and `scripts/make_log.py` writes a sample log into it.
- `legacy/` is the code before the rewrite, kept until every reader of it is gone. Nothing new imports it.
