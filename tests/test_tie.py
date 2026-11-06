import pytest

from runlog.cli import main

ROWS = """run_id,date,model,learning_rate,epochs,val_accuracy,val_loss
r001,2026-09-01,resnet18,0.001,10,0.903,0.335
r004,2026-09-04,distilbert,0.00003,5,0.912,0.287
r003,2026-09-03,resnet50,0.0005,20,0.912,0.287
r002,2026-09-02,bert-base,0.00002,3,0.912,0.301
"""


@pytest.fixture
def tied_csv(tmp_path):
    path = tmp_path / "tied.csv"
    path.write_text(ROWS, encoding="utf-8")
    return path


def run_ids(out):
    return [line.split()[0] for line in out.splitlines()]


def test_best_breaks_a_tie_on_lower_loss_then_earlier_date(tied_csv, capsys):
    assert main(["--data", str(tied_csv), "best"]) == 0
    assert run_ids(capsys.readouterr().out) == ["r003"]


def test_top_ranks_ties_the_same_way(tied_csv, capsys):
    assert main(["--data", str(tied_csv), "best", "--top", "4"]) == 0
    assert run_ids(capsys.readouterr().out) == ["r003", "r004", "r002", "r001"]


def test_report_names_the_same_best_run(tied_csv, capsys):
    assert main(["--data", str(tied_csv), "report"]) == 0
    best_line = capsys.readouterr().out.splitlines()[1]
    assert best_line.startswith("best: r003 ")
