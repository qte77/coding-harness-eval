# Spike #22 — Dependency De-risking (2026-06)

Resolves the dependency unknowns that gate the harness build (issue #22). Covers
**bullet 1 (`cc-recursive-team-mode`)**, which is the only #22 item that gates the scaffold (#8)
and models (#9), plus (2026-10-25) **Codebuff's headless mode** and **current Anthropic pricing**.
Headless modes for the other agents are largely answered by Harbor (#57); the repo-baseline
payload audit (→ #25) stays open under #22.

## `cc-recursive-team-mode` — install method + API

**Verified (2026-06-14, via the public repo `qte77/cc-recursive-team-mode`):**

- **Not published to PyPI.** It is a public **git** project, installed as a dev dependency via
  `uv` (its own `make setup_dev`), i.e. a `git+https://…` dependency, not `pip install cc-recursive-team-mode`.
- **Import name:** `cc_recursive` (note: distribution name uses dashes, import uses underscores).
- **Public Python API:** `from cc_recursive import run, RunConfig, RunProfile`.
  - `run(config: RunConfig) -> RunResult`
  - `RunResult` (Pydantic) carries: `exit_code: int`, `tokens: int`, `cost_usd: float`,
    `tool_calls: list`.
  - Helpers: `load_prompt()`, `parse_session()` (parses Claude session artifacts).
- **Headless CLI wrapper:** `scripts/cc-recursive-team.sh` (drive without Python).

## Decision

Declare `cc-recursive-team-mode` as a **git-based optional dependency** under
`[project.optional-dependencies].agents`, **not** in the CI-synced `dev` group.

**Why:**
- CI runs `uv sync --group dev`, which does not install optional extras → the git dependency
  cannot redden CI (and we avoid resolving a git URL on every CI run).
- It is not *used* until the Claude Code collector (#10) shells out to `cc_recursive.run()` —
  so wiring it now would be speculative (YAGNI). #10 installs the `agents` extra and consumes
  the API documented above.

**Consumption note for #10:** prefer the Python API (`run(RunConfig) -> RunResult`) over the
shell wrapper so `exit_code`/`tokens`/`cost_usd`/`tool_calls` come back typed; map those onto the
harness `RunResult`/`TokenUsage` models. `parse_session()` may cover the transcript-JSONL token
split.

## Codebuff — headless mode

**Verified (2026-10-25, at source):**

- **No print / headless / JSON flag.** The CLI option definitions in
  [`cli/src/cli-args.ts`](https://github.com/CodebuffAI/codebuff/blob/main/cli/src/cli-args.ts)
  have no `-p` / `--print` / `--output-format` / `--json` equivalent. The `codebuff` CLI (npm
  package `codebuff`, bins `codebuff` and `cb`) accepts an initial prompt as a positional
  argument (`[prompt...]`, "Initial prompt to send to the agent") plus `--agent <agent-id>`,
  `--max`, `--plan`, `--lite`, `--cwd <directory>` and `--trust-agents` ("for CI"). Per
  freebuff#947 below it still starts the interactive terminal UI and stdin piping hangs on a TTY
  (**unverified**, not run here). The free `freebuff` build accepts no prompt argument at all.
- **Headless route is the SDK.** [`@codebuff/sdk`](https://github.com/CodebuffAI/codebuff/blob/main/sdk/README.md):
  `new CodebuffClient({ apiKey, cwd })` then `client.run({ agent, prompt, handleEvent })`; the
  `handleEvent` callback streams messages, tool calls and errors. Needs a Codebuff API key
  (`CODEBUFF_API_KEY` in the README example).
- A print-mode flag is requested upstream in
  [CodebuffAI/freebuff#947](https://github.com/CodebuffAI/freebuff/issues/947) (open, no maintainer
  reply as of 2026-10-25).

**Implication for #11:** the generic CLI-subprocess collector cannot drive Codebuff headless.
Either a small Node shim around `@codebuff/sdk` (needs a Codebuff API key) or dropping Codebuff from the
Phase-1 agent set is an owner decision.

## Anthropic pricing (per MTok, USD)

**Verified (2026-10-25)** at <https://platform.claude.com/docs/en/about-claude/pricing> (Claude API,
first-party, global routing; retired and limited-availability Mythos models omitted):

| Model | Base input | 5m cache write | 1h cache write | Cache hit / refresh | Output |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Claude Fable 5.1 | $10 | $12.50 | $20 | $0.25 | $50 |
| Claude Fable 5 | $10 | $12.50 | $20 | $1 | $50 |
| Claude Opus 5.5 | $4 | $5 | $8 | $0.20 | $20 |
| Claude Opus 5 | $5 | $6.25 | $10 | $0.50 | $25 |
| Claude Opus 4.8 / 4.7 / 4.6 / 4.5 | $5 | $6.25 | $10 | $0.50 | $25 |
| Claude Sonnet 5.5 | $2 | $2.50 | $4 | $0.10 | $10 |
| Claude Sonnet 5 | $2 | $2.50 | $4 | $0.20 | $10 |
| Claude Sonnet 4.6 / 4.5 | $3 | $3.75 | $6 | $0.30 | $15 |
| Claude Haiku 5.5 (prompt up to 100k tokens) | $0.10 | $0.125 | $0.20 | $0.01 | $0.50 |
| Claude Haiku 5.5 (prompt over 100k tokens) | $0.50 | $0.625 | $1 | $0.05 | $2.50 |
| Claude Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 |

Modifiers that affect harness cost estimates (same source):

- Cache hits are 0.025x base input on Fable 5.1, 0.05x on Opus 5.5 / Sonnet 5.5, 0.1x elsewhere.
- Batch API is 50% of the base input/output rates.
- US-only inference (`inference_geo`) is a 1.1x multiplier on all token categories (4.6 and later).
- Fast mode: Opus 5.5 $8 / $40, Opus 5 and 4.8 $10 / $50 (input / output).
- Claude 4.7 and later use a newer tokenizer (about 30% more tokens for the same text), so
  token counts are not comparable across that boundary.

Re-verify at run time; the cost estimator should read rates from config, not hard-code them.
