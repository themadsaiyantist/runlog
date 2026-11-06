# runlog

A small command-line tool over `runs.csv`, a log of training runs with one row per run: its id, the date, the model, the learning rate, the epochs, and the validation accuracy and loss. It reads the file with the standard library and prints what you ask for.

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pytest
.venv/bin/python -m runlog best
.venv/bin/python -m runlog report
.venv/bin/python -m pytest
```

`best` prints the run with the highest validation accuracy. `report` prints how many runs there are, the best one, and the mean accuracy of every model. Both take `--data PATH` to read another file instead of `runs.csv`.

## How the project works

- `runs.csv` is built from the exports in `data/raw/` by `scripts/import_raw.py`. A change to the data goes into a raw export and the script, never into `runs.csv` by hand.
- `data/raw/` holds the exports exactly as the training machine wrote them, and nothing edits them.
- The standard library only: `csv`, `argparse`, `dataclasses`. No pandas.
- Every change comes with a test in `tests/`, and `pytest` passes before a commit.
- Model names are lowercase, as the exports write them.
- `logs/` is gitignored, and `scripts/make_log.py` writes a sample log into it.
- `legacy/` is the code before the rewrite, kept until every reader of it is gone. Nothing new imports it.
