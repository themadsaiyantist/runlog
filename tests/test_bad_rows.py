import pytest

from runlog.cli import main
from runlog.data import load_runs

HEADER = "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"
GOOD = "r001,2026-09-01,resnet18,0.001,10,0.871,0.412\n"


@pytest.mark.parametrize("bad_row", [
    "r002,2026-09-02,resnet18,0.0005,20,0.903\n",      # a field short
    "r002,2026-09-02\n",                               # many fields short
    "r002,2026-09-02,resnet18,0.0005,20,,0.335\n",     # an empty field
])
@pytest.mark.parametrize("command", [["best"], ["report"], ["report", "--format", "md"]])
def test_a_row_with_a_missing_field_is_a_clean_error(tmp_path, capsys, bad_row, command):
    path = tmp_path / "runs.csv"
    path.write_text(HEADER + GOOD + bad_row, encoding="utf-8")
    assert main(["--data", str(path), *command]) == 1
    err = capsys.readouterr().err
    assert err.startswith("runlog: ")
    assert "line 3" in err


def test_load_runs_names_the_missing_field(tmp_path):
    path = tmp_path / "runs.csv"
    path.write_text(HEADER + GOOD + "r002,2026-09-02,resnet18,0.0005,20,0.903\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"line 3: missing value for \['val_loss'\]"):
        load_runs(path)


def test_an_unreadable_number_names_its_line(tmp_path):
    path = tmp_path / "runs.csv"
    path.write_text(HEADER + GOOD + "r002,2026-09-02,resnet18,0.0005,twenty,0.903,0.335\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 3"):
        load_runs(path)
