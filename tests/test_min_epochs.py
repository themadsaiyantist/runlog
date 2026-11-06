from runlog.cli import main


def test_best_min_epochs_keeps_runs_with_that_many_epochs(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--min-epochs", "10", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert [line.split()[0] for line in out.splitlines()] == ["r002", "r001"]
