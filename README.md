# sweeps

A small sweep runner. It reads a grid of settings from `sweep.toml`, expands it into one configuration per combination, runs each through a fake trainer that scores it deterministically from a seed, writes the scores as the `runs.csv` that `runlog` reads, and reports the best.

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pytest
.venv/bin/python -m sweeps expand
.venv/bin/python -m sweeps run --out runs.csv
.venv/bin/python -m sweeps report --data runs.csv
.venv/bin/python -m pytest
```

`expand` prints every configuration the grid produces. `run` runs them all and writes the CSV, four at a time with `--parallel 4`, and `--dry-run` prints what it would run without running it. `report` prints how many runs there are, the best one, and the mean accuracy of every model. Both `expand` and `run` take `--config PATH` to read another sweep file.

## The sweep file

```toml
[sweep]
name = "resnet-lr-epochs"
seed = 42

[grid]
model = ["resnet18", "resnet50"]
learning_rate = [0.01, 0.001, 0.0001]
epochs = [5, 10]
```

The seed defaults to 42 when the file gives none. Every list under `[grid]` is one axis, and the run order follows the keys as written.
