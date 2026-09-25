"""Pydantic data contracts for the coding-harness-eval harness.

AgentBeats-compatible result schema with N=3 variance (mean + ``*_stddev``), token
counts split by type, and a per-run sandbox ``isolation_tier``. See
``docs/architecture.md`` and ``docs/research/landscape-security-sandbox-2026-06.md``.
All models are strict and frozen so results are validated on construction and
immutable once produced.
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_STRICT = ConfigDict(strict=True, frozen=True)


class IsolationTier(StrEnum):
    """Sandbox isolation tier recorded per run; publishable results require ``T2``."""

    T0 = "T0"
    T1 = "T1"
    T2 = "T2"


class TokenUsage(BaseModel):
    """Token counts split by type, per the metrics methodology (incl. cache)."""

    model_config = _STRICT

    prompt: int = Field(ge=0, description="Prompt (input) tokens.")
    completion: int = Field(ge=0, description="Completion (output) tokens.")
    cache_read: int = Field(default=0, ge=0, description="Tokens read from prompt cache.")
    cache_write: int = Field(default=0, ge=0, description="Tokens written to prompt cache.")

    @property
    def total(self) -> int:
        """Sum of all token types."""
        return self.prompt + self.completion + self.cache_read + self.cache_write


class GraderResult(BaseModel):
    """Outcome of a single grader for one run."""

    model_config = _STRICT

    grader: str = Field(description="Grader name, e.g. 'validate' or 'diff'.")
    score: float = Field(ge=0.0, le=1.0, description="Normalized grader score in [0, 1].")
    passed: bool = Field(description="Whether the grader's pass condition was met.")
    details: str = Field(default="", description="Human-readable grader detail.")


class ExpectedSolution(BaseModel):
    """Pointer to a spec's canonical solution.

    M1 (locked, #23): a sibling directory of the fixture's ``broken`` tree. M2 (single SUT repo
    with ``base_ref``/``solution_ref`` pairs) is tracked in #34. See ``docs/spec-schema.md``.
    """

    model_config = _STRICT

    solution_dir: str = Field(
        default="solution",
        description="Directory under `fixture` holding the canonical fixed tree.",
    )


class SpecConfig(BaseModel):
    """Parsed spec definition (``specs/S0N-<name>.json``); the runner↔specs contract (#23)."""

    model_config = _STRICT

    id: str = Field(description="Spec identifier, e.g. 'S01'.")
    name: str = Field(description="Short human-readable spec name.")
    prompt: str = Field(description="Task prompt handed to the agent.")
    target_files: list[str] = Field(
        default_factory=list,
        description="Paths the spec expects to change; drives scope_grader / scope_adherence.",
    )
    fixture: str | None = Field(
        default=None,
        description="Path to the fixture dir; the agent starts in `<fixture>/broken/`. "
        "None for a pure-prompt spec.",
    )
    expected_solution: ExpectedSolution | None = Field(
        default=None,
        description="Canonical solution for solution_grader; None runs validate_grader only.",
    )

    @model_validator(mode="after")
    def _solution_requires_fixture(self) -> Self:
        if self.expected_solution is not None and self.fixture is None:
            raise ValueError("expected_solution requires a fixture to resolve it against")
        return self


class RunResult(BaseModel):
    """AgentBeats-compatible aggregate for one ``(agent, spec)`` over ``run_count`` runs.

    Numeric metrics are means across the repeated runs; each carries a matching
    ``*_stddev`` capturing variance (N=3 by default).
    """

    model_config = _STRICT

    agent: str = Field(description="Agent identifier, e.g. 'claude'.")
    spec: str = Field(description="Spec identifier, e.g. 'S01'.")
    run_count: int = Field(ge=1, description="Number of repeated runs aggregated (N).")
    correctness: float = Field(ge=0.0, le=1.0, description="Mean weighted grader score.")
    correctness_stddev: float = Field(
        default=0.0, ge=0.0, description="Stddev of correctness across runs."
    )
    scope_adherence: float = Field(
        ge=0.0, le=1.0, description="Mean fraction of changes within expected paths."
    )
    scope_adherence_stddev: float = Field(
        default=0.0, ge=0.0, description="Stddev of scope_adherence across runs."
    )
    wall_time_s: float = Field(ge=0.0, description="Mean wall-clock seconds per run.")
    wall_time_s_stddev: float = Field(
        default=0.0, ge=0.0, description="Stddev of wall_time_s across runs."
    )
    cost_usd: float = Field(ge=0.0, description="Mean estimated USD cost per run.")
    cost_usd_stddev: float = Field(
        default=0.0, ge=0.0, description="Stddev of cost_usd across runs."
    )
    tokens: TokenUsage = Field(description="Mean token usage split by type.")
    tokens_stddev: float = Field(
        default=0.0, ge=0.0, description="Stddev of total tokens across runs."
    )
    turn_count: int = Field(ge=0, description="Mean agent turns / tool calls.")
    files_changed: int = Field(ge=0, description="Mean number of files modified.")
    isolation_tier: IsolationTier = Field(
        description="Sandbox tier used; T2 required for publishable results."
    )
    grader_results: list[GraderResult] = Field(
        default_factory=list, description="Per-grader breakdown."
    )


class SpecResult(BaseModel):
    """Aggregated results for one spec across all agents."""

    model_config = _STRICT

    spec: str = Field(description="Spec identifier.")
    runs: list[RunResult] = Field(
        default_factory=list, description="One RunResult per agent for this spec."
    )


class HarnessConfig(BaseModel):
    """Global harness configuration."""

    model_config = _STRICT

    agents: list[str] = Field(description="Agent identifiers to evaluate.")
    specs: list[str] = Field(description="Spec identifiers to run.")
    results_dir: str = Field(default="results", description="Directory for result JSON output.")
    run_count: int = Field(default=3, ge=1, description="Repeated runs per (agent, spec).")
    target_isolation_tier: IsolationTier = Field(
        default=IsolationTier.T2, description="Desired sandbox tier (auto-fallback to T1)."
    )
