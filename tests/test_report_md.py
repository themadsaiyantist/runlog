from runlog.cli import main


def test_report_md_prints_a_markdown_table(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report", "--format", "md"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# runlog report\n")
    assert "Runs: 4" in out
    assert "| Model | Mean accuracy |" in out
    assert "| bert-base | 0.904 |" in out


def test_report_text_stays_the_default(runs_csv, capsys):
    assert main(["--data", str(runs_csv), "report"]) == 0
    assert capsys.readouterr().out.startswith("runs: 4")
