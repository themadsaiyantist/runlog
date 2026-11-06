import pytest

from runlog.cli import main


def test_best_since_keeps_runs_from_that_date_on(runs_csv, capsys):
    # r003 (2026-09-03) is the best run overall; from 2026-09-04 on only r004 is left.
    assert main(["--data", str(runs_csv), "best", "--since", "2026-09-04", "--top", "5"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["r004"]


def test_since_includes_the_date_itself(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--since", "2026-09-02", "--top", "5"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["r003", "r002", "r004"]


def test_report_since_counts_only_the_kept_runs(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report", "--since", "2026-09-03"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "runs: 2"
    assert "resnet18" not in out


def test_report_md_since_counts_only_the_kept_runs(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report", "--format", "md", "--since", "2026-09-03"]) == 0
    assert "resnet18" not in capsys.readouterr().out


@pytest.mark.parametrize("command", ["best", "report"])
def test_since_after_the_last_run_fails(runs_csv, capsys, command):
    assert main(["--data", str(runs_csv), command, "--since", "2026-09-05"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")


@pytest.mark.parametrize("command", ["best", "report"])
@pytest.mark.parametrize("bad", ["yesterday", "2026-9-05", "05/09/2026", "20260905", "2026-02-30", "2026-09-05T10:00:00", ""])
def test_since_it_cannot_read_fails(runs_csv, capsys, command, bad):
    assert main(["--data", str(runs_csv), command, "--since", bad]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")
