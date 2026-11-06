import pytest

from runlog.cli import main

HEADER = "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"


@pytest.mark.parametrize("fmt", ["text", "md"])
def test_report_on_a_log_with_no_runs_says_so(tmp_path, capsys, fmt):
    path = tmp_path / "empty.csv"
    path.write_text(HEADER, encoding="utf-8")
    assert main(["--data", str(path), "report", "--format", fmt]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")
