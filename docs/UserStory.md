---
title: User Story - coding-harness-eval
description: User stories for hands-off coding agent comparison harness
category: requirements
created: 2026-03-22
updated: 2026-03-22
version: 1.0.0
---

# User Story: coding-harness-eval

## Problem Statement

There is no standardized way to compare coding agents (Claude Code, Cline, opencode, Codebuff, Gemini CLI) on identical tasks with consistent metrics. Each agent has different invocation methods, output formats, and configuration approaches, making apples-to-apples comparison impossible without a unified harness.

## Target Users

AI researchers comparing coding agent performance across standardized tasks.

## Value Proposition

Run any coding agent on any spec with a single command, collect consistent metrics, and generate comparison tables — enabling data-driven agent selection and configuration optimization.

## User Stories

- As a researcher, I want to run a single agent on a single spec so that I can verify the harness works end-to-end.
- As a researcher, I want to run all agents on all specs in batch so that I can generate a full comparison matrix.
- As a researcher, I want to view a comparison table as a markdown report so that I can quickly assess relative agent performance.
- As a researcher, I want to add a new agent to the harness so that I can extend comparisons to emerging tools.
- As a researcher, I want to add a new spec/task so that I can evaluate agents on different problem types.
- As a researcher, I want to run CC in recursive team mode via cc-recursive-team-mode so that I can compare solo vs team CC performance.

## Success Criteria

1. `make run AGENT=claude SPEC=S01-validate` produces `results/claude-S01.json` with correctness, wall_time, tokens, and cost fields.
2. `make run-all` executes all agent-spec combinations and writes results to `results/`.
3. `make compare` generates `results/comparison.md` with a table of all agents x specs x metrics.
4. Adding a new agent requires only creating an `agents/<name>/phase1/` config directory and a collector entry.
5. Adding a new spec requires only creating a `specs/S0N-<name>.json` file.
6. CC teams mode runs via cc-recursive-team-mode with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

## Constraints

- Python 3.13+
- Depends on cc-recursive-team-mode for CC subprocess management
- Git worktree isolation per run (no cross-contamination between agent runs)
- Each agent must run headless (no interactive prompts)

## Out of Scope

- LLM-as-judge grader (use deterministic graders only in Phase 1)
- Non-CLI agents (IDE plugins, web-based agents)
- Claude Agent SDK integration (Phase 2)
- Browser-based E2E testing (Playwright/Selenium)
