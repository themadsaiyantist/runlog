"""Expanding a grid of settings into every combination."""

from __future__ import annotations

from itertools import product


def expand(grid: dict[str, list]) -> list[dict]:
    """Every combination of the grid's values, one dict per run, the keys in the order the file lists them."""
    keys = list(grid)
    return [dict(zip(keys, values)) for values in product(*(grid[key][:-1] for key in keys))]
