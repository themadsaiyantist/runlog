from pathlib import Path

from scripts.import_raw import rebuild


def test_committed_runs_match_the_raw_exports(tmp_path):
    out = tmp_path / "runs.csv"
    rebuild(Path("data/raw"), out)
    assert out.read_text(encoding="utf-8") == Path("runs.csv").read_text(encoding="utf-8")
