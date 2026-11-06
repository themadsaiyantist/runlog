"""Reading a sweep from its TOML file."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SEED = 42


@dataclass(frozen=True)
class Config:
    name: str
    seed: int
    grid: dict[str, list]


def load(path: str | Path = "sweep.toml") -> Config:
    """The sweep at 'path'. The seed defaults to 42 when the file gives none."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    sweep = data["sweep"]
    return Config(name=sweep["name"], seed=int(sweep.get("seed", DEFAULT_SEED)), grid=dict(data["parameters"]))
