# coding-harness-eval

> Hands-off coding-agent comparison harness

[![License](https://img.shields.io/badge/license-Apache--2.0-58f4c2.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![CodeQL](https://github.com/qte77/coding-harness-eval/actions/workflows/codeql.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/codeql.yaml)
[![ruff](https://github.com/qte77/coding-harness-eval/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/ruff.yaml)
[![pyright](https://github.com/qte77/coding-harness-eval/actions/workflows/pyright.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/pyright.yaml)
[![pytest](https://github.com/qte77/coding-harness-eval/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/pytest.yaml)
[![complexipy](https://github.com/qte77/coding-harness-eval/actions/workflows/complexipy.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/complexipy.yaml)
[![links](https://github.com/qte77/coding-harness-eval/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/qte77/coding-harness-eval/actions/workflows/links-fail-fast.yaml)

## What

- Runs CC, Cline, opencode, Codebuff, and Antigravity CLI headless on identical specs
- Collects structured metrics: correctness, wall time, tokens, cost, turn count, scope adherence
- Generates comparison reports across all agent-spec combinations
- Grader package: `Grader` ABC + `ValidateGrader` and `ScopeGrader` implemented; `SolutionGrader` stubbed (TDD red, implementation pending)
- Phase 0 in progress: graders-first slice done; collector and runner implementation pending
- Already present: `Makefile`, `Makefile.python`, `research/` submodule, `LICENSE`, `SECURITY.md`

## How

```bash
# Run a single agent on a single spec
make run AGENT=claude SPEC=S01-validate

# Run all agent-spec combinations
make run-all

# Generate comparison report
make compare
```

These commands are Phase-0 placeholders; runner and collector implementation is pending. See [docs/architecture.md](docs/architecture.md) for the full data flow.

## Why

Comparing coding agents is usually ad-hoc and manual — each tool gets run under different conditions, making results incomparable. This harness runs them hands-off on identical specs under the same environment, producing apples-to-apples metrics for informed agent selection.

## References

- [docs/architecture.md](docs/architecture.md)
- [`cc-recursive-team-mode`](https://github.com/qte77/cc-recursive-team-mode)
- [`multi-tasking-quality-benchmark`](https://github.com/qte77/multi-tasking-quality-benchmark)
- [`ai-agents-research`](https://github.com/qte77/ai-agents-research)
- [An Open Agentic Coding Harness](https://qte77.github.io/open-agentic-coding-harness/)

## License

Apache-2.0 - see [LICENSE](LICENSE).
