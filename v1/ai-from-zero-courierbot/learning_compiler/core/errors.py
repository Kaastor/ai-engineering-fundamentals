"""Project-wide exception types.

We keep a small taxonomy of explicit exceptions so failures are visible and testable.
"""
from __future__ import annotations

from dataclasses import dataclass


class LearningCompilerError(Exception):
    """Base exception for this repository."""


class BudgetExceededError(LearningCompilerError):
    """Raised when a run exceeds an explicit budget/stop rule."""


class ToolError(LearningCompilerError):
    """Base error raised when a tool invocation fails."""


class ToolTimeoutError(ToolError):
    """Raised when a tool times out (simulated)."""


class ToolValidationError(ToolError):
    """Raised when a tool response fails schema/contract validation."""


class ToolPermissionError(ToolError):
    """Raised when the agent requests a tool that is not allowed."""


@dataclass(frozen=True, slots=True)
class InvariantViolationError(LearningCompilerError):
    """Raised when a system invariant is violated.

    We model invariants as *data*, because a run journal should capture the exact violation type.
    """

    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.message}"
