---
title: Landscape, Security & Sandbox Research — coding-harness-eval
description: Consolidated state analysis, arena landscape, repo-baseline security adoption, and agent-sandbox decisions
category: research
created: 2026-06-13
updated: 2026-06-13
version: 1.0.0
---

# Landscape, Security & Sandbox Research

Consolidated findings produced before building `coding-harness-eval` (a hands-off harness that runs CLI
coding agents headless on identical specs, collects metrics, and produces comparison reports). Analyzed
across five multi-agent research rounds, each adversarially verified. The repo is at **Phase 0** (docs +
scaffold; no `src/`).

## Locked decisions

- **Direction:** Standalone CLI harness (no A2A / Docker / platform coupling now).
- **Runs:** N=3 per (agent, spec) with mean + stddev / variance reporting.
- **Result format:** AgentBeats-compatible JSON (so a future platform submission is a thin wrapper, not a rewrite).
- **Sandbox:** pluggable backend; aim for T2 cloud microVM everywhere, auto-fallback to T1; publishable ⇒ T2.

---

## 1. Current project state (verified)

`main` = 2 commits (docs only); the full `docs/architecture.md` tree (`src/harness/*`, `specs/`, `agents/`,
`tests/`, `pyproject.toml`, `scripts/compare.py`) is missing. README Quick-Start is a placeholder.
Verified: `qte77/ai-agents-research` remote exists (PR #17 unblocked); `cc-recursive-team-mode` dep repo
exists (API unconfirmed).

**Issues (20 → 8 canonical + 2 WakaTime):** close thin dups #1→#10, #2→#9, #3 (out of scope), #4→#11+#13,
#5→#12+#14, #7→#15; retitle #10. Keep chain **#8→#9→#10→#11→#12→#13→#14→#15**; #6/#20 off critical path.
**PRs:** merge **#16 → #17 → #18**. **License:** 3-way mismatch (file BSD-3-Clause, README MIT, target
Apache-2.0 via #18) → post-merge `git mv LICENSE.md LICENSE`, fix refs, close #19.

## 2. Reusable tooling from `ai-agents-research`

`lib/monitor_utils.py` → drop-in scope/spec-adherence scorer (zero deps); `changelog-compare.py` → per-task
grading-report shape; transcript-JSONL parsing → tokens/cost/turns/wall-time (4 token types incl. cache);
`ccusage` → per-run cost; `repomix --compress` → spec fixtures; `code-review-graph` → structural blast-radius
scope check. Methodology: deterministic Phase-1 grading; keep `correctness` and `scope_adherence` separate;
k≥3 runs; no-op-agent integrity probe; split the 4 token types; pin pricing to run date.

## 3. Sibling repos = AgentBeats arena scenarios

`RDI-AgentBeats-MAS-GraphJudge` and `RDI-AgentBeats-TestBehaveAlign` are AgentBeats Green(judge)↔Purple(subject)
A2A scenarios — a different axis than our CLI harness. **MAS-GraphJudge** (multi-agent coordination via NetworkX
graph + LLM-judge + latency); best steals: `record_provenance.py`, evaluator ABC, LLM-judge-with-fallback.
**TestBehaveAlign** (test quality via mutation testing + fault detection, `0.6·mutation + 0.4·fault_detection`);
best steals: the network-blocked tempdir test runner + pure-function composite scorers. Shared **AgentBeats
output schema** = our chosen result format.

## 4. Coding-agent arena landscape (web, verified)

**AgentBeats** (agentbeats.dev, Berkeley RDI; open; has a **Coding** category) — the platform the siblings
target; a future submission path. **Terminal-Bench/Harbor** (Stanford×Laude, self-hostable, runs Claude
Code/Codex/Gemini CLI). **Artificial Analysis** (best cost+token+wall-time index). **OpenCode Bench**
(3-judge variance scoring). Cline Bench / KiloBench / Copilot Arena (UC Berkeley). TB 2.1: Codex CLI #1,
Claude Code #2, Gemini CLI ~71%. **⚠ Gemini CLI → Antigravity CLI rename 2026-06-18** — affects the `gemini`
collector. Differentiation holds: CLI tools as black-box subprocesses on dev-authored specs with deterministic
validate+diff + scope-adherence.

## 5. Security: `repo-baseline` adoption

**Verdict — sound and safe to adopt** for Free/Pro-tier-applicable controls. Some strongest controls (Required
Workflows, org CodeQL merge-gate, non-provider secret scanning) need Team/Enterprise tier and silently no-op
otherwise.

**⚠ Scripts are NOT safe to run as-is** (adversarial verdict). `extract-uses.sh` = SAFE (read-only).
`apply.sh`/`bulk-apply.sh` = SAFE-WITH-NOTES individually but execute whatever HTTP method the payload
`_meta.endpoint.method` declares (incl. `DELETE`/destructive `PUT`) with no dry-run/confirmation, plus a latent
jq-injection at `apply.sh:110`. Mitigation: audit each `NN-*.json` payload's method+endpoint; run single payloads
explicitly (e.g. payload 02); add a `--dry-run` mode.

**Top repo-level adoptions** (no org admin needed):

- **P1:** SHA-pin every `uses:` across all 9 workflows (currently floating `@vN`); replace `codeql.yaml` with the
  baseline (v3→v4, post-merge→`push` trigger); fix `pull_request: types:[closed]` (post-merge) triggers on
  ruff/pyright/pytest/complexipy; apply Payload 02 (`default_workflow_permissions: read`, no PR self-approve).
  Prefer org-reusable workflows pinned to a full SHA — e.g. replace `links-fail-fast.yaml` with a `lint-md-links.yml`
  calling `qte77/.github/.github/workflows/lint-md-links.yml@<SHA>` with `permissions: {contents: read}` and
  pre-merge triggers, per the reference `polyfetch-scrape/.github/workflows/lint-md-links.yml`.
- **P2:** swap Dependabot to the uv variant + add `github-actions` ecosystem + grouping; apply Payloads 04+05
  (`allowed_actions: selected`, `sha_pinning_required`, allowlist via `extract-uses.sh`); add Ruff `S` (bandit)
  ruleset; fix `.gitignore` (`results/` referenced as ignored but isn't).
- **P3:** Payload 03 (signed/immutable `v*` tags); explicit top-level `permissions: {}`; harden `write-llms-txt.yaml`
  `CONVERTER_URL` (unvalidated URL → committed content).
- **P4 (org admin):** enable 2FA + Dependabot alerts org-wide; apply Payload 06 subset (PR gate + signatures +
  linear history work at Free tier; `code_scanning`/`code_quality` rules need Team+).

**The baseline does NOT cover this project's core risk — running untrusted agents as subprocesses.** Extra,
repo-specific controls (reported by the posture agent):

- **Sandbox** each agent subprocess via a pluggable `Sandbox` backend (ABC, mirroring Collector/Grader) with a
  tier roadmap:
  - **T0 (bring-up):** git worktree + each CLI's native sandbox (Claude Code bwrap/Seatbelt = off by default;
    Codex CLI seccomp/Landlock = on) + secrets via mitmproxy/env-scrub + per-worktree venv.
  - **T1 (local default):** rootless Podman + netns + seccomp + per-agent iptables egress allowlist (resolve
    LLM-API IPs at session start, default-DROP, block RFC1918/loopback/IMDS) + mitmproxy sidecar holding the API key.
  - **T2 (publishable):** Firecracker microVM (E2B or Fly Sprites) + DNS egress allowlist + snapshot provenance.

  Two orthogonal axes drive the tier: (1) **threat level** (semi-trusted vs adversarial) is intrinsic to the
  agents/tasks and sets the minimum tier everywhere — an adversarial agent (or untrusted code it fetches, e.g.
  `npm install`) threatens the local box too, not just public runs; (2) **evidentiary bar** — T2's microVM is
  additionally required for publishable results because a shared-kernel container can't make an unfalsifiable
  isolation claim. **Decision (locked): aim for T2, auto-fall back to T1.** Implement T2 as a cloud microVM
  (E2B / Fly Sprites) — remote isolation works from inside this repo's `.devcontainer/` where local userns/nested-virt
  is blocked; fall back to T1 only when cloud creds are absent or for fast offline iteration. Record an
  `isolation_tier` per run; publishable results require T2. Gate `--dangerously-skip-permissions` behind an explicit
  env flag.
- **Fix `SECURITY.md`** — it points to the upstream template repo, not `qte77/coding-harness-eval`.

## 6. Open blockers / de-risk spikes

1. `cc-recursive-team-mode` install + API (gates #8/#9/#10).
2. Headless modes for Cline/opencode/Codebuff + Gemini→Antigravity binary name (gates #11).
3. Lock the `spec.json` schema (`expected_diff` = unified-diff text, file list, or commit SHA?) — define first.
4. Audit L1 payload HTTP methods before any `apply.sh` run.
5. Agent-sandbox is researched (`ai-agents-research/docs/cc-native/sandboxing/*` already covers Fly Sprites/E2B/
   gVisor/bwrap — apply, don't re-research). Implementation notes: per-agent egress allowlist + `isolation_tier`.
6. Re-verify Anthropic pricing at run time.

## 7. Recommended forward plan (ordered)

**Status (2026-06-20):** graders-first slice progressed — `ValidateGrader` and `ScopeGrader` implemented; `SolutionGrader` spec'd with xfail tests (TDD red, impl pending).

- **Step 1 — Repo hygiene + CI security quick-wins:** merge #16→#17→#18; license `git mv` + close #19; close dup
  issues + retitle #10; SHA-pin all actions, swap in baseline `codeql.yaml`, fix post-merge triggers, apply Payload
  02 (after auditing), swap Dependabot→uv, add Ruff `S`, fix `.gitignore` + `SECURITY.md`.
- **Step 2 — De-risk spikes (§6):** confirm `cc-recursive-team-mode` API, agent headless modes + Antigravity binary,
  lock `spec.json` schema, audit L1 payloads, decide sandbox approach. Output: a decisions note.
- **Step 3 — Scaffold:** #8 `pyproject.toml` (uv, Py 3.13, `cc-recursive-team-mode`, Ruff `S`) + #9 Pydantic models
  in AgentBeats-compatible schema with `run_count`/`*_stddev` (N=3) + an `isolation_tier` field.
- **Step 4 — Implement Phase-1 harness (#10–#15):** adopt §2 tools + §3 `record_provenance.py`, multi-column
  `comparison.md` (correctness | time | cost | tokens | scope), and the §5 sandbox controls before any real
  untrusted-agent run.

### Items to confirm during execution (defaults in brackets)

License → Apache-2.0 + `LICENSE` rename · Payload 06 tier behavior (apply trimmed subset) · sandbox scope
(all runtimes vs. opt-in flag) · `results/` gitignore policy.

## 8. Verification

- PRs: `gh pr checks <n>`; post-merge `git submodule update --init --recursive`. License: `git show HEAD:LICENSE`
  = Apache-2.0; #19 closed. Issues: `gh issue list --state open` = 8 canonical + #6/#20.
- CI security: every `uses:` is a full SHA; CodeQL runs on `push` pre-merge; `gh api` shows
  `default_workflow_permissions=read`. Scripts: dry-run/payload audit before `apply.sh`.
- Agent isolation: a probe agent cannot read another worktree's `/tmp` secrets, escape its worktree, or mutate a
  shared venv.
- Spikes: `cc-recursive-team-mode` imports in a throwaway venv; each agent CLI runs one headless task; current
  Gemini/Antigravity binary confirmed.

---

## Verification provenance

Adversarial web verification across the research rounds corrected several claims; carry these forward: SWE-bench is
Princeton NLP (not Princeton/Stanford); Copilot Arena is UC Berkeley/LMSYS (not CMU); Terminal-Bench is Stanford×Laude
(Harbor is only the runner); the "DevBench" arxiv id `2512.12216` is actually SWE-Playground; Fly's "$0.07/CPU-hr"
itemized pricing is fabricated (Fly uses bundled pricing); Fly Sprites already ships a Python SDK; Modal has TS+Go SDKs
(not Python-only); Daytona's network allowlist takes CIDRs, not domains.
