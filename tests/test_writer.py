from sweeps.writer import write_csv

ROW = {"run_id": "r001", "date": "2026-11-06", "model": "resnet18", "learning_rate": 0.001, "epochs": 10, "val_accuracy": 0.9, "val_loss": 0.2}


def test_write_csv_uses_the_header_runlog_reads(tmp_path):
    path = tmp_path / "runs.csv"
    assert write_csv([ROW], path) == 1
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss"
    assert lines[1].startswith("r001,2026-11-06,resnet18")
