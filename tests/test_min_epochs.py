import pytest

from runlog.cli import main


def test_best_min_epochs_keeps_runs_with_that_many_epochs(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--min-epochs", "10", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert [line.split()[0] for line in out.splitlines()] == ["r002", "r001"]


def test_best_min_epochs_combines_with_model(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--model", "ResNet18", "--min-epochs", "15", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert [line.split()[0] for line in out.splitlines()] == ["r002"]


def test_best_min_epochs_combines_with_since(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--since", "2026-09-02", "--min-epochs", "10", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert [line.split()[0] for line in out.splitlines()] == ["r002"]


def test_best_min_epochs_with_no_runs_left_names_the_threshold(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--min-epochs", "100"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "runlog: no runs with at least 100 epochs\n"


@pytest.mark.parametrize(
    "args",
    [
        ["--model", "bert-base", "--min-epochs", "10"],
        ["--since", "2026-09-03", "--min-epochs", "10"],
    ],
)
def test_best_min_epochs_with_no_runs_left_fails(runs_csv, capsys, args):
    assert main(["--data", str(runs_csv), "best", *args]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")
