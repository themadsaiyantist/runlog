import pytest

from runlog.data import Run, load_runs


def test_load_runs_reads_every_row_in_order(runs_csv):
    runs = load_runs(runs_csv)
    assert [run.run_id for run in runs] == ["r001", "r002", "r003", "r004"]


def test_load_runs_parses_numbers(runs_csv):
    first = load_runs(runs_csv)[0]
    assert first == Run("r001", "2026-09-01", "resnet18", 0.001, 10, 0.871, 0.412)


def test_load_runs_refuses_a_missing_column(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("run_id,model\nr001,resnet18\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_runs(path)
