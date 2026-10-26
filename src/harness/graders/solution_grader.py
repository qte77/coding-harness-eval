"""SolutionGrader — diff overlap vs the canonical expected_solution.

Computes partial credit (hunk/line overlap, #12): the fraction of changed lines in the
canonical diff (``broken`` -> ``solution``) that the agent's diff also reproduces.
A changed line is ``(path, "+"|"-", text)`` with whitespace collapsed, so pure
formatting differences do not cost credit; blank lines are ignored.

Behaviour:
- ``None`` expected_solution  -> skipped (score 1.0, passed True, details "skipped").
- Empty canonical diff        -> score 1.0 (nothing to reproduce).
- Otherwise                   -> ``len(agent_lines & canonical_lines) / len(canonical_lines)``.
"""

import difflib
import subprocess
from pathlib import Path

from harness.graders.base import Grader
from harness.models import GraderResult, SpecConfig

_BROKEN_DIR = "broken"

type ChangedLine = tuple[str, str, str]


def _normalize(line: str) -> str:
    return " ".join(line.split())


def _diff_lines(path: str, old: str, new: str) -> set[ChangedLine]:
    """Changed lines between two file versions, whitespace-normalized."""
    a = [_normalize(line) for line in old.splitlines()]
    b = [_normalize(line) for line in new.splitlines()]
    changed: set[ChangedLine] = set()
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            changed |= {(path, "-", text) for text in a[i1:i2] if text}
            changed |= {(path, "+", text) for text in b[j1:j2] if text}
    return changed


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _tree_files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def _canonical_lines(broken: Path, solution: Path) -> set[ChangedLine]:
    changed: set[ChangedLine] = set()
    for rel in _tree_files(broken) | _tree_files(solution):
        changed |= _diff_lines(rel, _read(broken / rel), _read(solution / rel))
    return changed


def _git(args: list[str], worktree: Path) -> str:
    proc = subprocess.run(  # noqa: S603 — fixed argv, trusted worktree path; S607 git on PATH
        ["git", *args],  # noqa: S607
        cwd=worktree,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout


def _agent_lines(worktree: Path) -> set[ChangedLine]:
    """Changed lines of ``git diff`` (tracked files, working tree vs baseline)."""
    changed: set[ChangedLine] = set()
    for rel in _git(["diff", "--name-only"], worktree).splitlines():
        baseline = _git(["show", f"HEAD:{rel}"], worktree)
        changed |= _diff_lines(rel, baseline, _read(worktree / rel))
    return changed


class SolutionGrader(Grader):
    """Structural partial credit: how much of the canonical fix did the agent reproduce?"""

    name = "solution"

    def grade(self, worktree: Path, spec: SpecConfig) -> GraderResult:
        """Score the agent's diff against the canonical solution diff.

        ``spec.fixture`` + ``spec.expected_solution.solution_dir`` locate the
        canonical solution tree (M1: sibling of ``broken/``).  The agent's diff
        is ``git diff`` (working tree vs baseline commit).

        Returns a ``GraderResult`` with ``score`` in ``[0, 1]``.
        """
        if spec.expected_solution is None or spec.fixture is None:
            return GraderResult(grader=self.name, score=1.0, passed=True, details="skipped")
        fixture = Path(spec.fixture)
        canonical = _canonical_lines(
            fixture / _BROKEN_DIR, fixture / spec.expected_solution.solution_dir
        )
        if not canonical:
            return GraderResult(
                grader=self.name, score=1.0, passed=True, details="empty canonical diff"
            )
        matched = len(_agent_lines(worktree) & canonical)
        return GraderResult(
            grader=self.name,
            score=matched / len(canonical),
            passed=matched == len(canonical),
            details=f"{matched}/{len(canonical)} canonical diff lines reproduced",
        )
