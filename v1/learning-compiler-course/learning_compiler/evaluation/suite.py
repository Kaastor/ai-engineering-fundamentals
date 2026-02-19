from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvalOutcome:
    passed: bool
    score: float | None
    details: str
    evidence: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class EvalCase:
    name: str
    run: Callable[[], EvalOutcome]


@dataclass(frozen=True, slots=True)
class CaseResult:
    name: str
    outcome: EvalOutcome


@dataclass(frozen=True, slots=True)
class SuiteResult:
    cases: tuple[CaseResult, ...]
    passed: int
    failed: int

    def all_passed(self) -> bool:
        return self.failed == 0

    def to_markdown(self) -> str:
        lines: list[str] = []
        lines.append(f"## Eval results: {self.passed} passed, {self.failed} failed")
        for cr in self.cases:
            status = "✅ PASS" if cr.outcome.passed else "❌ FAIL"
            score = "" if cr.outcome.score is None else f" (score={cr.outcome.score:.3f})"
            lines.append(f"- {status} **{cr.name}**{score}: {cr.outcome.details}")
            if cr.outcome.evidence:
                for k, v in cr.outcome.evidence:
                    lines.append(f"  - {k}: {v}")
        return "\n".join(lines)


def run_suite(cases: Sequence[EvalCase]) -> SuiteResult:
    results: list[CaseResult] = []
    passed = 0
    failed = 0

    for case in cases:
        try:
            outcome = case.run()
        except Exception as exc:  # noqa: BLE001 - evaluation should surface exceptions
            outcome = EvalOutcome(
                passed=False,
                score=None,
                details=f"Exception: {type(exc).__name__}: {exc}",
                evidence=(),
            )

        results.append(CaseResult(name=case.name, outcome=outcome))
        if outcome.passed:
            passed += 1
        else:
            failed += 1

    return SuiteResult(cases=tuple(results), passed=passed, failed=failed)
