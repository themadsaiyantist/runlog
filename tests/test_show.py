from runlog.cli import main


def test_show_prints_every_column_in_csv_order(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "show", "r003"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "run_id: r003",
        "date: 2026-09-03",
        "model: bert-base",
        "learning_rate: 0.00002",
        "epochs: 3",
        "val_accuracy: 0.912",
        "val_loss: 0.301",
    ]


def test_show_keeps_the_csv_column_order_and_extra_columns(tmp_path, capsys):
    path = tmp_path / "runs.csv"
    path.write_text(
        "val_loss,run_id,notes,date,model,learning_rate,epochs,val_accuracy\n"
        "0.4,r9,warm start,2026-09-01,resnet18,0.001,10,0.87\n",
        encoding="utf-8",
    )
    assert main(["--data", str(path), "show", "r9"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split(":")[0] for line in lines] == [
        "val_loss", "run_id", "notes", "date", "model", "learning_rate", "epochs", "val_accuracy",
    ]
    assert "notes: warm start" in lines


def test_show_an_id_not_in_the_file_fails(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "show", "r999"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")


def test_show_prints_a_good_run_when_another_row_does_not_parse(tmp_path, capsys):
    path = tmp_path / "runs.csv"
    path.write_text(
        "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"
        "r001,2026-09-01,resnet18,0.001,10,0.871,0.412\n"
        "r002,2026-09-02,resnet18,0.0005,3.0,,\n",
        encoding="utf-8",
    )
    assert main(["--data", str(path), "show", "r001"]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "run_id: r001"
    assert main(["--data", str(path), "show", "r002"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "val_loss: "
