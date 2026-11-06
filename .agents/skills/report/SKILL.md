---
name: report
description: Writes the run report for runlog, a Markdown summary of runs.csv saved in reports/. Use when the user asks for a run report, a status update on the training runs, or how the runs are going.
---

# The run report

Run all commands from the repository root. Read an optional cutoff date from
the user's request, such as `since 2026-08-15`; there is no argument variable.

1. Run `.venv/bin/python .agents/skills/report/render.py` for all runs. If the
   request supplies a cutoff date, pass just that date as the single positional
   argument: `.venv/bin/python .agents/skills/report/render.py 2026-08-15`.
   Do not pass the word `since` or a `--since` flag to the renderer. It prints the
   whole report with every number filled in. If it fails, show the error and stop.
2. Read `.agents/skills/report/guide.md`, and replace the two TODO lines as it
   says. Change nothing else.
3. Save the result as `reports/YYYY-MM-DD.md`, using the report title's current
   date. When a cutoff date was given, use `reports/YYYY-MM-DD-since-DATE.md`
   instead, with that requested cutoff date as DATE.
4. Do not commit. Reply with the path and the summary line.
