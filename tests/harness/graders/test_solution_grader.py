"""Tests for SolutionGrader — diff overlap vs the canonical expected_solution.

Fixture layout (M1 contract):
    tmp_path/
      fixture/
        broken/   <- starting state (agent worktree is a copy of this, git-initialised)
        solution/ <- canonical fix
      worktree/   <- git repo; agent has edited files here
"""

import subprocess
from pathlib import Path

from harness.graders.solution_grader import SolutionGrader
from harness.models import ExpectedSolution, SpecConfig

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(  # noqa: S603 — fixed argv, trusted tmp_path
        ["git"] + args,  # noqa: S607
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def _make_fixture(tmp_path: Path, broken_files: dict, solution_files: dict) -> Path:
    """Create broken/ and solution/ subtrees under tmp_path/fixture/."""
    fixture = tmp_path / "fixture"
    for subdir, files in [("broken", broken_files), ("solution", solution_files)]:
        d = fixture / subdir
        d.mkdir(parents=True)
        for name, content in files.items():
            (d / name).write_text(content, encoding="utf-8")
    return fixture


def _make_worktree(tmp_path: Path, baseline_files: dict, edited_files: dict) -> Path:
    """Create a git repo in tmp_path/worktree/ with a baseline commit, then apply edits.

    Uses -c commit.gpgsign=false so the test repo ignores any global signing requirement.
    """
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    _git(["init", "-b", "main"], worktree)
    _git(["config", "user.email", "test@example.com"], worktree)
    _git(["config", "user.name", "Test"], worktree)
    _git(["config", "commit.gpgsign", "false"], worktree)
    for name, content in baseline_files.items():
        (worktree / name).write_text(content, encoding="utf-8")
    _git(["add", "."], worktree)
    _git(["commit", "-m", "baseline"], worktree)
    for name, content in edited_files.items():
        (worktree / name).write_text(content, encoding="utf-8")
    return worktree


def _spec(fixture: Path) -> SpecConfig:
    return SpecConfig(
        id="S0",
        name="n",
        prompt="p",
        fixture=str(fixture),
        expected_solution=ExpectedSolution(solution_dir="solution"),
    )


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_no_expected_solution_is_skipped(tmp_path: Path):
    """None expected_solution -> score 1.0, passed True, details 'skipped'."""
    # No git repo needed: grader should return 'skipped' before touching the worktree.
    spec = SpecConfig(id="S0", name="n", prompt="p")

    result = SolutionGrader().grade(tmp_path, spec)

    assert result.score == 1.0
    assert result.passed
    assert "skipped" in result.details.lower()


def test_perfect_match_scores_one(tmp_path: Path):
    """Agent reproduces the entire canonical diff -> score 1.0."""
    broken = {"bug.py": "x = 1\n"}
    solution = {"bug.py": "x = 2\n"}
    fixture = _make_fixture(tmp_path, broken, solution)
    worktree = _make_worktree(tmp_path, broken, solution)
    spec = _spec(fixture)

    result = SolutionGrader().grade(worktree, spec)

    assert result.score == 1.0
    assert result.passed


def test_partial_match_returns_fraction(tmp_path: Path):
    """Agent fixes only part of the required changes -> score is a proper fraction."""
    # canonical fix: two lines change; agent fixes only one
    broken = {"a.py": "x = 1\ny = 1\n"}
    solution = {"a.py": "x = 2\ny = 2\n"}
    fixture = _make_fixture(tmp_path, broken, solution)
    # agent only changes x, not y
    worktree = _make_worktree(tmp_path, broken, {"a.py": "x = 2\ny = 1\n"})
    spec = _spec(fixture)

    result = SolutionGrader().grade(worktree, spec)

    assert 0.0 < result.score < 1.0
    assert not result.passed


def test_whitespace_only_differences_still_match(tmp_path: Path):
    """Agent's fix differs from the canonical one only in whitespace -> score 1.0."""
    broken = {"a.py": "def f():\n    return 1\n"}
    solution = {"a.py": "def f():\n    return 2\n"}
    fixture = _make_fixture(tmp_path, broken, solution)
    worktree = _make_worktree(tmp_path, broken, {"a.py": "def f():\n\treturn  2\n"})
    spec = _spec(fixture)

    result = SolutionGrader().grade(worktree, spec)

    assert result.score == 1.0
    assert result.passed


def test_zero_overlap_scores_zero(tmp_path: Path):
    """Agent changes files not in the canonical diff -> score 0.0."""
    broken = {"a.py": "x = 1\n"}
    solution = {"a.py": "x = 2\n"}
    fixture = _make_fixture(tmp_path, broken, solution)
    # agent changes a completely different file
    worktree = _make_worktree(tmp_path, broken, {"other.py": "y = 99\n"})
    spec = _spec(fixture)

    result = SolutionGrader().grade(worktree, spec)

    assert result.score == 0.0
    assert not result.passed
