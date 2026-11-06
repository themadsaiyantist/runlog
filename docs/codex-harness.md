# Codex harness

`AGENTS.md` is the single source of shared project instructions for both tools.
`CLAUDE.md` imports it with `@AGENTS.md`, and `docs/conventions.md` links to its
conventions section. The tool configurations and shared hook scripts are unchanged.

## Setup and hooks

Use the existing Python 3.12 `.venv` with pytest installed. Install `uv` to make
`uvx mcp-server-fetch` available. `.codex/config.toml` registers the same fetch
server as `.mcp.json`; this does not install or contact it.

Trust the project and review the three hooks through `/hooks` in Codex before
using them. Project configuration and hook trust are separate checks. Codex
skips unreviewed hooks. See the [official hooks documentation](https://learn.chatgpt.com/docs/hooks).

The commands in `.codex/hooks.json` change to the Git root before invoking the
existing scripts, so a session started in a subdirectory still uses the root
`.venv`. No Claude environment variable is needed.

The documented Codex stdin/output contract matches these scripts:

| Event | Relevant input | Existing behavior |
| --- | --- | --- |
| `PreToolUse` | Shell execution, including `exec_command`, becomes `tool_name: "Bash"` with `tool_input.command` | Gate commits; exit 2 and stderr block a failing commit |
| `SessionStart` | `source` matches `startup`, `clear`, or `compact`; common fields include `cwd` | Print branch and test results as model context |
| `Stop` | Boolean `stop_hook_active` | Exit 2 and stderr request continuation on failures; skip a repeated stop |

The start matcher preserves the Claude configuration; it does not add `resume`
or `fork`. `tests/test_codex_harness.py` exercises these payloads and configured
commands from a subdirectory with spaces in its path. These are contract tests,
not a live model session or a test of Codex's own dispatcher.

## Report skill

Invoke `$report` or ask for a training run report. For example:
`$report since 2026-08-15`. Codex reads the cutoff from the request and runs
`.venv/bin/python .agents/skills/report/render.py 2026-08-15` from the root.
Without a cutoff it runs the same command without a positional argument.

The guide and renderer are independent copies of the Claude versions. The
renderer still supplies today's report date; the requested date is the run
cutoff. Only the Summary and Next placeholders are edited, and the skill never
commits. See the [official skills documentation](https://developers.openai.com/codex/skills).

## Features without a direct translation

- `${CLAUDE_SKILL_DIR}` and `$ARGUMENTS` have no Codex substitution here. The
  skill uses repository-root paths and reads the request. Claude's
  `argument-hint` metadata is omitted; the usage example is in the instructions.
- Claude `permissions.allow/ask/deny` and local permission settings are not
  Codex config keys. Codex uses its own permissions and command rules. The raw
  data edit restriction and push approval requirement are retained as
  `AGENTS.md` instructions, not equivalent enforcement. No automatic grants for
  pytest, runlog, or uv were added.
- `worktree.baseRef: "head"` and the test writer's `isolation: worktree` have no
  direct mapping in these Codex agent files. Prepare a worktree explicitly if
  isolation is required. Codex also has its own [worktree workflow](https://learn.chatgpt.com/docs/environments/git-worktrees).
- The two agent prompts are translated to `.codex/agents/*.toml`. Claude model
  aliases `sonnet` and `opus` are not Codex model names; the agents inherit the
  parent model. `disallowedTools: Write, Edit, NotebookEdit` has no direct
  equivalent in these definitions. The reviewer retains the no-edit instruction,
  but inherits the parent's permissions. See [custom agents and permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- `.claude/workflows/review-runlog.js` is not executable by Codex's configuration
  loader. There is no direct loader for its `pipeline`, `agent`, phase UI, and
  schema declarations. Rebuilding that orchestration needs a separate skill or
  SDK program; it is left in Claude's harness. Codex subagents can perform the
  reviews, but the JavaScript is not registered as a Codex workflow.
- Claude private memory and `CLAUDE.local.md` are not imported. This repository
  does not contain a `CLAUDE.local.md`; the workflow's host-rename memory remains
  inside its original workflow rather than becoming a new project-wide rule.

No commit is made by this migration. The Codex test writer reports its work and
commits only when the user's request authorizes it.
