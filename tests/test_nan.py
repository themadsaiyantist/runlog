import pytest

from runlog.cli import main
from runlog.data import load_runs
from runlog.report import best_run, top_runs

HEADER = "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"


def write(tmp_path, rows):
    path = tmp_path / "runs.csv"
    path.write_text(HEADER + "".join(rows), encoding="utf-8")
    return path


@pytest.mark.parametrize("order", [0, 1, 2])
def test_a_nan_accuracy_is_never_the_best_run(tmp_path, order):
    rows = ["r001,2026-09-01,resnet18,0.001,10,0.871,0.412\n",
            "r002,2026-09-02,resnet18,0.0005,20,0.903,0.335\n"]
    rows.insert(order, "r009,2026-09-09,resnet18,0.1,10,nan,nan\n")
    runs = load_runs(write(tmp_path, rows))
    assert best_run(runs).run_id == "r002"
    assert [run.run_id for run in top_runs(runs, 3)] == ["r002", "r001"]


def test_best_and_report_skip_a_nan_accuracy(tmp_path, capsys):
    path = write(tmp_path, ["r009,2026-09-09,resnet18,0.1,10,NaN,0.5\n",
                            "r001,2026-09-01,resnet18,0.001,10,0.871,0.412\n"])
    assert main(["--data", str(path), "best"]) == 0
    assert capsys.readouterr().out.startswith("r001 ")
    assert main(["--data", str(path), "report"]) == 0
    assert capsys.readouterr().out.splitlines()[1].startswith("best: r001 ")


def test_every_accuracy_nan_is_a_clean_error(tmp_path, capsys):
    path = write(tmp_path, ["r009,2026-09-09,resnet18,0.1,10,nan,0.5\n"])
    assert main(["--data", str(path), "best"]) == 1
    assert capsys.readouterr().err.startswith("runlog: no runs with a validation accuracy")


def test_a_nan_loss_loses_a_tie(tmp_path):
    runs = load_runs(write(tmp_path, ["r001,2026-09-01,resnet18,0.001,10,0.9,nan\n",
                                      "r002,2026-09-02,resnet18,0.001,10,0.9,0.4\n"]))
    assert best_run(runs).run_id == "r002"
