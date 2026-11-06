from runlog.cli import main
from runlog.data import load_runs
from runlog.report import mean_accuracy_by_model, summary


def test_mean_accuracy_by_model_is_sorted_by_name(runs_csv):
    means = mean_accuracy_by_model(load_runs(runs_csv))
    assert list(means) == ["bert-base", "resnet18"]
    assert means["resnet18"] == (0.871 + 0.903) / 2


def test_summary_names_the_count_and_the_best(runs_csv):
    text = summary(load_runs(runs_csv))
    assert text.startswith("runs: 4\nbest: r003")
    assert "mean accuracy by model:" in text


def test_report_command_prints_the_summary(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report"]) == 0
    assert capsys.readouterr().out.startswith("runs: 4")
