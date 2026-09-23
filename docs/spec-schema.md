# Spec schema (`specs/S0N-<name>.json`)

The locked contract between the runner (#13) and authored specs (#14). Source of truth is
`SpecConfig` in `src/harness/models.py`; this doc explains intent and the fixture mechanism.

## Fields

| Field | Type | Purpose |
|---|---|---|
| `id` | `str` | Spec identifier, e.g. `"S01"`. |
| `name` | `str` | Short human-readable name, e.g. `"fix-bug"`. |
| `prompt` | `str` | Task prompt handed to the agent. |
| `target_files` | `list[str]` | Paths the spec expects to change → `scope_grader` / `scope_adherence`. |
| `fixture` | `str \| None` | Path to the fixture dir; the agent starts in `<fixture>/broken/`. `None` = pure-prompt spec. |
| `expected_solution` | `ExpectedSolution \| None` | Canonical answer key for `solution_grader`. `None` → only `validate_grader` (+ `scope_grader`) run. |

`ExpectedSolution`: `{ solution_dir: str = "solution" }` — a directory under `fixture` holding
the canonical fixed tree. **Invariant:** `expected_solution` requires `fixture` (validated).

Note the deliberate split: `target_files` answers *"which files may change?"* (scope);
`expected_solution` answers *"what is the correct change?"* (correctness). They feed different
graders and are independent.

## Fixture mechanism (M1)

Each fixture is a self-contained mini-project in two states:

```
fixtures/
  S02-fix-bug/
    broken/      # the project with the bug; `make validate` FAILS
    solution/    # the canonical fix; `make validate` PASSES
```

Per run (fresh per N, so variance is real):

1. Copy `<fixture>/broken/` into an isolated temp worktree; `git init` + commit = baseline.
2. Run the agent headless in that worktree (sandboxed, #26); it edits files.
3. `agent_diff = git diff` (worktree vs baseline) — agents need not commit.
4. Grade:
   - `validate_grader` — `make validate` in the worktree → `1.0` / `0.0` (behavioral correctness).
   - `solution_grader` — overlap of `agent_diff` with `diff(broken → solution)` → `[0,1]`
     (structural partial credit; only if `expected_solution` is set).
   - `scope_grader` — agent's changed paths vs `target_files` → `scope_adherence`.

`validate_grader` and `solution_grader` are intentionally distinct: *"is it correct?"* (binary)
vs *"how close to the canonical fix?"* (partial credit), so they don't measure the same thing.

## Example

```json
{
  "id": "S02",
  "name": "fix-bug",
  "prompt": "paginate() drops the last item. Fix the off-by-one.",
  "target_files": ["src/pagination.py"],
  "fixture": "fixtures/S02-fix-bug",
  "expected_solution": { "solution_dir": "solution" }
}
```

A validate-only spec (e.g. `S01`) omits `expected_solution` (and may still set `fixture` to run
the agent against a broken project graded purely by `make validate`).

## Deferred: M2 fixture delivery (#34)

M1 stores broken/solution as plain directories — transparent and self-contained, at the cost of
duplication. M2 (single SUT git repo with `base_ref`/`solution_ref` tag pairs) is tracked in
[#34](https://github.com/qte77/coding-harness-eval/issues/34); it changes only `ExpectedSolution`
(dir → refs) and the runner's checkout step.
