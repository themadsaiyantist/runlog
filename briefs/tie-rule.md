# The tie rule

Goal: when two runs tie on validation accuracy, the one with the lower validation loss ranks higher. If the loss ties too, the earlier date ranks higher, and only then does file order decide. `best`, `best --top N` and the best line of `report`, in both formats, rank runs this one way, so they always agree.

Files: the ranking lives in runlog/report.py, in best_run and top_runs. tests/test_tie.py describes the rule.

Constraints: the standard library only. No change to the CSV format, to the printed formats, or to any test. Keep best_run and top_runs as the names the rest of the code calls.

Done: tests/test_tie.py passes unchanged, the whole suite passes with .venv/bin/python -m pytest, `best`, `best --top 3` and `report` agree on the real runs.csv, and nothing is committed.
