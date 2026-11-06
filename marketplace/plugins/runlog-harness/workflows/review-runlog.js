export const meta = {
  name: 'review-runlog',
  description: 'Review runlog/ for correctness, tests and conventions; verify each finding with a second agent',
  phases: [
    { title: 'Review', detail: 'one read-only reviewer per dimension' },
    { title: 'Verify', detail: 'one skeptic per dimension checks every finding' },
  ],
}

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string', description: 'repo-relative path' },
          line: { type: 'integer' },
          title: { type: 'string' },
          detail: { type: 'string', description: 'what is wrong and why' },
          scenario: { type: 'string', description: 'concrete input/state -> wrong result, or the specific rule broken' },
        },
        required: ['file', 'line', 'title', 'detail', 'scenario'],
      },
    },
  },
  required: ['findings'],
}

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          index: { type: 'integer' },
          verdict: { type: 'string', enum: ['CONFIRMED', 'PLAUSIBLE', 'REFUTED'] },
          evidence: { type: 'string', description: 'what you ran or read that settles it' },
        },
        required: ['index', 'verdict', 'evidence'],
      },
    },
  },
  required: ['verdicts'],
}

const TARGET = (typeof args === 'string' && args.trim()) ? args.trim() : 'runlog/'

const SCOPE = TARGET === 'runlog/'
  ? `Scope: the Python package in runlog/ (cli.py, data.py, report.py, __main__.py), with tests/ and docs/conventions.md as reference. It is small (~230 lines) — read it all.`
  : `Scope: the folder ${TARGET}, with tests/ and docs/conventions.md as reference. Read all of it.`

const COMMON = `${SCOPE} Do NOT modify any file. You may run the tool (.venv/bin/python -m runlog ...) and tests (.venv/bin/python -m pytest -q) to check behaviour; use the scratchpad for any temp files, never the repo. Report only real issues with a concrete file:line; no style nits, no speculation. An empty list is a fine answer.`

const DIMENSIONS = [
  { key: 'correctness', prompt: `Review for CORRECTNESS bugs: wrong results, crashes on plausible input (empty CSV, missing/blank fields, ties, bad numbers, unknown run id), off-by-one, wrong comparisons, argparse mistakes. For each, give a concrete input that produces the wrong output.` },
  { key: 'tests', prompt: `Review TEST COVERAGE: behaviour in ${TARGET} that no test in tests/ exercises, and tests whose assertions are too weak to catch a regression in what they claim to test. For each, name the untested code path (file:line) and the scenario a missing test should cover.` },
  { key: 'conventions', prompt: `Review against the project CONVENTIONS in docs/conventions.md and CLAUDE.md: standard library only (no pandas/new deps); model names lowercased before comparison wherever a user types one; every behaviour having a test. Also respect the project memory: gpu-01 was renamed gpu-a (same machine) and raw exports keep gpu-01 — check whether code handling hosts accounts for that. For each, quote the rule broken and the code that breaks it.` },
]

const results = await pipeline(
  DIMENSIONS,
  d => agent(`${d.prompt}\n\n${COMMON}`, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS, agentType: 'runlog-harness:reviewer' }),
  (review, d) => {
    const fs = (review && review.findings) || []
    if (!fs.length) return { key: d.key, findings: [] }
    const list = fs.map((f, i) => `[${i}] ${f.file}:${f.line} — ${f.title}\n${f.detail}\nScenario: ${f.scenario}`).join('\n\n')
    return agent(`You are an independent skeptic verifying ${d.key} findings another reviewer made about ${TARGET}. Try to REFUTE each one. Read the cited code yourself; where possible reproduce it (run the CLI on a scratch CSV, or a throwaway test in the scratchpad). For coverage claims, grep tests/ to see whether a test already covers it. Verdict: CONFIRMED (you reproduced it or the code unambiguously shows it), PLAUSIBLE (likely real but not demonstrated), REFUTED (wrong, already handled, or already tested). Default to REFUTED if the claim misreads the code.\n\n${COMMON}\n\nFindings:\n\n${list}`,
      { label: `verify:${d.key}`, phase: 'Verify', schema: VERDICTS, effort: 'low' })
      .then(v => ({ key: d.key, findings: fs.map((f, i) => {
        const vv = ((v && v.verdicts) || []).find(x => x.index === i)
        return { ...f, verdict: vv ? vv.verdict : 'UNVERIFIED', evidence: vv ? vv.evidence : '' }
      }) }))
  },
)

return results.filter(Boolean)