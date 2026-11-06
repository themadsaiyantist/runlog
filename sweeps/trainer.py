"""A fake trainer: a deterministic score for a configuration, so a sweep runs in milliseconds."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass

BASE = {"resnet18": 0.86, "resnet50": 0.88, "bert-base": 0.90, "distilbert": 0.87}


@dataclass(frozen=True)
class Result:
    val_accuracy: float
    val_loss: float


def train(config: dict, seed: int) -> Result:
    """The score of 'config' under 'seed'. The same pair always gives the same result."""
    rng = random.Random(f"{seed}:{json.dumps(config, sort_keys=True)}")
    base = BASE.get(str(config.get("model")), 0.80)
    learning_rate = float(config.get("learning_rate", 0.001))
    epochs = int(config.get("epochs", 10))
    lr_penalty = abs(math.log10(learning_rate) + 3) * 0.02
    epoch_gain = min(epochs, 20) * 0.002
    accuracy = max(0.0, min(0.99, base - lr_penalty + epoch_gain + rng.uniform(-0.01, 0.01)))
    loss = max(0.02, 1.1 - accuracy + rng.uniform(-0.03, 0.03))
    return Result(round(accuracy, 3), round(loss, 3))
