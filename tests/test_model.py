import pytest

from runlog.cli import main


def run_ids(out):
    return [line.split()[0] for line in out.splitlines()]


def test_best_model_keeps_only_that_model(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--model", "resnet18", "--top", "5"]) == 0
    assert run_ids(capsys.readouterr().out) == ["r002", "r001"]


def test_best_model_lowercases_the_name_typed(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--model", "ResNet18"]) == 0
    assert run_ids(capsys.readouterr().out) == ["r002"]


def test_best_model_combines_with_since(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--model", "bert-base", "--since", "2026-09-04"]) == 0
    assert run_ids(capsys.readouterr().out) == ["r004"]


@pytest.mark.parametrize("args", [["--model", "vit"], ["--model", "resnet18", "--since", "2026-09-03"]])
def test_best_model_with_no_runs_left_fails(runs_csv, capsys, args):
    assert main(["--data", str(runs_csv), "best", *args]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")


@pytest.mark.parametrize("fmt", ["text", "md"])
def test_report_model_keeps_only_that_model(runs_csv, capsys, fmt):
    assert main(["--data", str(runs_csv), "report", "--format", fmt, "--model", "ResNet18"]) == 0
    out = capsys.readouterr().out
    assert ("runs: 2" if fmt == "text" else "Runs: 2") in out
    assert "r002" in out
    assert "bert-base" not in out


def test_report_model_combines_with_since(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report", "--model", "bert-base", "--since", "2026-09-04"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "runs: 1"
    assert out.splitlines()[1].startswith("best: r004 ")


@pytest.mark.parametrize("args", [["--model", "vit"], ["--model", "resnet18", "--since", "2026-09-03"]])
def test_report_model_with_no_runs_left_fails(runs_csv, capsys, args):
    assert main(["--data", str(runs_csv), "report", *args]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")
