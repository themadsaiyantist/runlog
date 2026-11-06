#!/usr/bin/env bash
# Write the run report with no one at the keyboard: the report skill, run by claude -p.
set -euo pipefail
cd "$(dirname "$0")/.."

out=$(claude -p "/report" \
  --output-format json \
  --permission-mode dontAsk \
  --allowedTools "Bash(.venv/bin/python *)" "Edit(/reports/**)" < /dev/null)

echo "$out" | python3 -c '
import json, sys
run = json.load(sys.stdin)
print(run["result"])
turns, cost, denied = run["num_turns"], run["total_cost_usd"], len(run.get("permission_denials", []))
print(f"turns: {turns}, cost: ${cost:.2f}, denied: {denied}")
sys.exit(1 if run["is_error"] else 0)
'
