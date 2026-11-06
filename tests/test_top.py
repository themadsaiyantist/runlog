from runlog.cli import main


def test_best_top_three_prints_three_runs_highest_first(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best", "--top", "3"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["r003", "r002", "r004"]


def test_best_without_top_still_prints_one_run(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "best"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 1
