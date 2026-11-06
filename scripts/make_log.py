"""Write logs/train.log, 5,000 lines of a fake training run, from a fixed seed so every student's counts match."""

from __future__ import annotations

import datetime
import random
from pathlib import Path

OUT = Path("logs/train.log")
SEED = 20261106
LINES = 5000
MESSAGES = {
    "INFO": [
        "loss={loss:.4f} lr={lr:g}",
        "val_accuracy={acc:.4f}",
        "checkpoint written to checkpoints/step_{step}.pt",
        "epoch {epoch} done in {seconds}s",
        "data loader fetched batch {batch}",
    ],
    "WARNING": [
        "gradient norm {norm:.1f} clipped to 1.0",
        "learning rate below 1e-06, training may stall",
        "batch {batch} had 3 empty samples, skipped",
    ],
    "ERROR": [
        "NaN loss at step {step}, batch discarded",
        "checkpoint write failed: disk quota exceeded",
        "data loader timed out after 30s, retrying",
    ],
}


def main() -> None:
    random.seed(SEED)
    OUT.parent.mkdir(exist_ok=True)
    start = datetime.datetime(2026, 9, 14, 8, 0, 0)
    lines = []
    step = 0
    for _ in range(LINES):
        level = random.choices(["INFO", "WARNING", "ERROR"], weights=[90, 7, 3])[0]
        step += random.randint(1, 3)
        text = random.choice(MESSAGES[level]).format(
            loss=max(0.02, 2.5 * 0.999**step + random.uniform(-0.05, 0.05)),
            lr=random.choice([0.001, 0.0005, 0.0001]),
            acc=min(0.99, 0.5 + step / 20000 + random.uniform(-0.02, 0.02)),
            step=step,
            epoch=step // 500,
            seconds=random.randint(40, 90),
            batch=step % 64,
            norm=random.uniform(1.5, 40.0),
        )
        stamp = (start + datetime.timedelta(seconds=step * 2)).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{stamp} {level:<7} step={step:<6} {text}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} lines to {OUT}")


if __name__ == "__main__":
    main()
