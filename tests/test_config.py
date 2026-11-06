from sweeps.config import load

TOML = """[sweep]
name = "demo"

[grid]
model = ["resnet18"]
learning_rate = [0.01, 0.001]
"""


def test_load_reads_the_name_and_the_grid(tmp_path):
    path = tmp_path / "sweep.toml"
    path.write_text(TOML, encoding="utf-8")
    cfg = load(path)
    assert cfg.name == "demo"


def test_seed_defaults_to_zero(tmp_path):
    path = tmp_path / "sweep.toml"
    path.write_text(TOML, encoding="utf-8")
    assert load(path).seed == 0
