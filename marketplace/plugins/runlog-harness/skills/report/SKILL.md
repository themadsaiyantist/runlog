---
name: report
description: Writes the run report for runlog, a Markdown summary of runs.csv saved in reports/. Use when the user asks for a run report, a status update on the training runs, or how the runs are going.
argument-hint: "[since YYYY-MM-DD]"
---

# The run report

1. Run `.venv/bin/python ${CLAUDE_SKILL_DIR}/render.py $ARGUMENTS`. It prints the whole report with every number filled in. If it fails, show the error and stop.
2. Read `${CLAUDE_SKILL_DIR}/guide.md`, and replace the two TODO lines as it says. Change nothing else.
3. Save the result as `reports/YYYY-MM-DD.md`, with today's date. When a date was given, save it as `reports/YYYY-MM-DD-since-DATE.md` instead.
4. Do not commit. Reply with the path and the summary line.
