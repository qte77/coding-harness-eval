---
title: TODO - coding-harness-eval
description: Implementation task tracker for the coding agent comparison harness
category: implementation
created: 2026-03-22
updated: 2026-03-22
version: 1.0.0
---

# TODO: coding-harness-eval

## Done

- [x] Template scaffold (Makefile, Makefile.python)
- [x] Research submodule (`research/` pointing to ai-agents-research)
- [x] LICENSE, SECURITY.md
- [x] Foundational docs (README.md, docs/UserStory.md, docs/architecture.md, docs/TODO.md)

## Next

- [ ] Pydantic models (`src/harness/models.py`) — HarnessConfig, SpecConfig, RunResult, GraderResult, SpecResult
- [ ] Collector ABC (`src/harness/collectors/base.py`)
- [ ] CC collector (`src/harness/collectors/cc_collector.py`) — wraps cc-recursive-team-mode
- [ ] Generic collector (`src/harness/collectors/generic_collector.py`) — direct CLI subprocess

## Backlog

- [ ] Grader ABC (`src/harness/graders/base.py`)
- [ ] Validate grader (`src/harness/graders/validate_grader.py`) — runs `make validate` in worktree
- [ ] Diff grader (`src/harness/graders/diff_grader.py`) — git diff vs spec expected
- [ ] Runner (`src/harness/runner.py`) — orchestrates worktree + collector + graders
- [ ] Specs: S01-validate, S02-fix-bug, S03-add-feature (`specs/`)
- [ ] Agent configs: claude, cline, opencode, codebuff, gemini phase1 dirs (`agents/`)
- [ ] Makefile targets: `run`, `run-all`, `compare`
- [ ] Comparison report generator (`results/comparison.md`)
- [ ] Unit tests for models, collectors, graders, runner

## Deferred

- [ ] LLM-as-judge grader (Phase 1 uses deterministic graders only)
- [ ] Non-CLI agents (IDE plugins, web-based agents)
- [ ] Phase 2 agent configs (teams, skills, hooks)
- [ ] Claude Agent SDK integration
- [ ] CC teams mode phase2 config (`agents/claude/phase2/`)
- [ ] Extended grader suite (Phase 2)
