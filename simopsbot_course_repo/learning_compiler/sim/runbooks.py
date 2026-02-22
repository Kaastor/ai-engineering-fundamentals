from __future__ import annotations

import random

from learning_compiler.sim.redteam import maybe_inject_untrusted_snippet
from learning_compiler.types import IncidentType


def runbook_search(*, incident: IncidentType, query: str, rng: random.Random) -> tuple[str, ...]:
    """Return synthetic runbook snippets.

    Intentionally includes:
    - partial info
    - occasional outdated/conflicting advice
    - occasional untrusted/injected text (for Meeting 5)
    """

    base = _incident_snippets(incident)
    distractors = _distractor_snippets()

    # A tiny "search": rank by word overlap, then pick top-k with noise.
    tokens = {t.lower() for t in query.split() if t.strip()}
    scored: list[tuple[int, str]] = []
    for s in base + distractors:
        score = sum(1 for t in tokens if t in s.lower())
        scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], x[1]))

    k = 3
    top = [s for _, s in scored[: k + 2]]
    rng.shuffle(top)
    snippets = tuple(top[:k])

    injected = maybe_inject_untrusted_snippet(rng=rng)
    if injected is None:
        return snippets
    return snippets + (injected,)


def _incident_snippets(incident: IncidentType) -> list[str]:
    if incident is IncidentType.API_BAD_DEPLOY:
        return [
            "If API error rate spikes after deploy, confirm version and consider rollback to v1.",
            "Restarting API may clear transient errors, but persistent 5xx suggests a bad deploy.",
            "Verification: after rollback, check API error rate < 5% and latency trending down.",
        ]
    if incident is IncidentType.DB_SATURATION:
        return [
            "DB saturation: elevated DB latency will cascade into API latency.",
            "First response: restart DB to clear runaway resource usage (toy system).",
            "Verification: DB latency should return near baseline within 2 checks.",
        ]
    if incident is IncidentType.NETWORK_FLAKY:
        return [
            "Flaky network shows up as timeouts in API logs while DB health may look OK.",
            "Mitigation: restart API to reset connection pools and retry logic (toy system).",
            "Verification: API timeout errors should drop after restart.",
        ]
    raise AssertionError(f"Unhandled incident: {incident}")


def _distractor_snippets() -> list[str]:
    return [
        "If you see 'disk full' errors, rotate logs and free space. (Not used in this toy world.)",
        "If CPU is high, consider autoscaling. (Not available in this lab simulator.)",
        "If latency is high, check upstream dependencies. (Yes, but not always the cause.)",
        "Old note (outdated): always restart API before any other step.",
    ]
