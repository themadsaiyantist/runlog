from runlog.cli import main
from runlog.data import load_runs
from runlog.report import best_run


def test_best_run_has_the_highest_accuracy(runs_csv):
    assert best_run(load_runs(runs_csv)).run_id == "r003"


def test_best_command_prints_the_best_run(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("r003  bert-base")
    assert "acc=0.912" in out


def test_best_command_fails_cleanly_on_a_missing_file(tmp_path, capsys):
    assert main(["--data", str(tmp_path / "nope.csv"), "best"]) == 1
    assert "runlog:" in capsys.readouterr().err
