"""Running every configuration of a sweep and collecting the rows runlog reads."""

from __future__ import annotations

import datetime

from .config import Config
from .grid import expand
from .ids import run_id
from .log import say
from .trainer import train


def run_all(cfg: Config) -> list[dict]:
    rows = []
    today = datetime.date.today().isoformat()
    for index, config in enumerate(expand(cfg.grid), start=1):
        result = train(config, cfg.seed)
        say(f"{run_id(index)} {config} acc={result.val_accuracy:.3f} loss={result.val_loss:.3f}")
        rows.append(
            {
                "run_id": run_id(index),
                "date": today,
                "model": config.get("model", ""),
                "learning_rate": config.get("learning_rate", ""),
                "epochs": config.get("epochs", ""),
                "val_accuracy": result.val_accuracy,
                "val_loss": result.val_loss,
            }
        )
    return rows
