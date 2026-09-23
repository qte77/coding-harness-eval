---
title: Phase-1 Harness Roadmap
description: Prioritized open work to complete the Phase-1 coding-harness-eval harness
category: planning
updated: 2026-06-14
---

# Phase-1 Harness Roadmap

Forward plan for completing the Phase-1 harness (run CLI agents headless on identical specs →
deterministic grading → comparison report). Sorted by what to do next.

**Foundation in place:** Pydantic models (#9), the `spec.json` schema (#23 — see `spec-schema.md`),
and the `validate` + `scope` graders (#12). Everything below is open, in order.

## Critical path (epic #24)

### 1. `solution_grader` — finish #12
The last grader. **Decide the overlap algorithm first:**

- (a) file-overlap — coarse; largely redundant with `scope_grader`.
- **(b) hunk / line-overlap (recommended)** — fraction of the canonical `diff(broken → solution)`
  reproduced in the agent's diff, whitespace/format-normalized; a real partial-credit signal.
- (c) behavioral apply-and-test — avoid; duplicates `validate_grader`'s pass/fail.

Operates on the M1 fixture `fixtures/<spec>/{broken,solution}/`. TDD. **Unblocked.**

### 2. CC collector — #10
Collector ABC + `cc_collector.py`. Wraps `cc-recursive-team-mode` (git-only `agents` extra;
`from cc_recursive import run, RunConfig`; `run() -> RunResult` carrying
`exit_code`/`tokens`/`cost_usd`/`tool_calls`) → map onto harness `RunResult`/`TokenUsage`. **Unblocked.**

### 3. Runner — #13
Orchestrate worktree → collector → graders → write `results/<agent>-<spec>.json`. First
end-to-end slice once #10 + graders exist.

### 4. Specs S01–S03 + M1 fixtures — #14
`fixtures/<spec>/{broken,solution}/` self-contained mini-projects (each with its own
`make validate`): S01 validate-only, S02 fix-bug, S03 add-feature.

### 5. Comparison report — #15
Multi-column `comparison.md` (correctness | time | cost | tokens | scope), N=3 mean + stddev.

## Enabler — spike #22 (run in parallel; gates the generic collector)

- Confirm headless `-p` / `--output-format` modes for Cline / opencode / Codebuff / Gemini, and the
  **Gemini → Antigravity** binary name → unblocks **#11 generic collector**.
- Re-verify Anthropic pricing; audit repo-baseline payloads (feeds #25).

## Cross-cutting (before any real untrusted-agent run)

- **#25** — CI / supply-chain hardening (SHA-pin actions, CodeQL v4, pre-merge triggers, Dependabot → uv).
- **#26** — pluggable `Sandbox` backend (aim T2 cloud microVM, fall back to T1; record `isolation_tier`).

## Deferred

- **#34** — M2 fixture delivery (single SUT repo + ref pairs) when M1 duplication bites.
- **#37** — re-introduce the Ralph loop for long-running E2E tasks.
- **#6 / #20** — WakaTime module + research (separate stream).

## Build conventions

- Strict TDD (red → green); **value-add tests only** (no default / getter / framework tests).
- `make validate` is the gate: ruff (incl. `S`) + pyright + complexipy + pytest @ 70% coverage.
- Models: Pydantic `strict=True, frozen=True`, with `Field` bounds + descriptions.
- `subprocess` calls: fixed argv (no shell); annotate `# noqa: S603,S607` with a reason.
