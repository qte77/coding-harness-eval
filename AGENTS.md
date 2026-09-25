# coding-harness-eval

Hands-off coding-agent comparison harness. Runs CC, Cline, opencode, Codebuff, and
Antigravity CLI headless on identical specs, collects structured metrics, and
generates comparison reports.

Phase 0: graders-first slice. The `Grader` ABC (named `Grader`, not BaseGrader) plus
`ValidateGrader` and `ScopeGrader` are implemented; `SolutionGrader` is a TDD-red stub
(xfail spec tests, implementation pending). Collector and runner are pending.

## Working here

- Python repo driven by Makefile recipes: `make run AGENT=<a> SPEC=<s>`, `make run-all`,
  `make compare`. See README.md and docs/architecture.md for data flow, metrics, and phases.
- Strict TDD: spec tests land first as xfail, then implement to green.
- `research/` is the ai-agents-research submodule; `results/` is gitignored output.

## Conventions

- Agent config is AGENTS.md-only; CLAUDE.md is a symlink to this file.
- Claude Code plugins are configured in .claude/settings.json against the
  qte77-claude-code-plugins marketplace; shared rules live in .claude/rules/.
