from runlog.cli import main

HEADER = "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"


def test_models_prints_each_model_and_its_run_count_sorted_by_name(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "models"]) == 0
    out = capsys.readouterr().out
    assert [line.split() for line in out.splitlines()] == [["bert-base", "2"], ["resnet18", "2"]]


def test_models_counts_runs_from_the_data_file(tmp_path, capsys):
    path = tmp_path / "other.csv"
    path.write_text(
        HEADER
        + "r1,2026-09-01,vit-small,0.001,10,0.8,0.4\n"
        + "r2,2026-09-02,albert,0.001,10,0.8,0.4\n"
        + "r3,2026-09-03,vit-small,0.001,10,0.8,0.4\n"
        + "r4,2026-09-04,vit-small,0.001,10,0.8,0.4\n",
        encoding="utf-8",
    )
    assert main(["--data", str(path), "models"]) == 0
    out = capsys.readouterr().out
    assert [line.split() for line in out.splitlines()] == [["albert", "1"], ["vit-small", "3"]]


def test_models_on_a_log_with_no_runs_fails(tmp_path, capsys):
    path = tmp_path / "empty.csv"
    path.write_text(HEADER, encoding="utf-8")
    assert main(["--data", str(path), "models"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"runlog: no runs in {path}\n"


def test_models_with_a_missing_file_fails(tmp_path, capsys):
    assert main(["--data", str(tmp_path / "nope.csv"), "models"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("runlog: ")
