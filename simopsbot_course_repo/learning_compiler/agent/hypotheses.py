from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.types import ConfidenceLevel, IncidentType, JSONValue


@dataclass(slots=True, frozen=True)
class Hypothesis:
    cause: IncidentType
    confidence: ConfidenceLevel
    evidence_ids: tuple[str, ...]


class Hypotheses:
    """Tiny hypothesis manager: 2–3 competing causes with evidence links.

    This is intentionally not probabilistic math. It is:
    - explicit uncertainty
    - evidence tracking
    - a disciplined trigger for "observe more" vs "act"
    """

    def __init__(self) -> None:
        self._score: dict[IncidentType, float] = {
            IncidentType.API_BAD_DEPLOY: 0.0,
            IncidentType.DB_SATURATION: 0.0,
            IncidentType.NETWORK_FLAKY: 0.0,
        }
        self._evidence: dict[IncidentType, list[str]] = {k: [] for k in self._score}

    def update_from_observation(self, *, obs: dict[str, JSONValue], evidence_event_id: str) -> None:
        tool = obs.get("tool")
        if tool == "get_metrics":
            self._update_from_metrics(obs=obs, evidence_event_id=evidence_event_id)
            return
        if tool == "tail_logs":
            self._update_from_logs(obs=obs, evidence_event_id=evidence_event_id)
            return
        if tool == "runbook_search":
            self._update_from_runbook(obs=obs, evidence_event_id=evidence_event_id)
            return

    def top(self, *, k: int = 3) -> tuple[Hypothesis, ...]:
        ranked = sorted(self._score.items(), key=lambda kv: (-kv[1], kv[0].value))
        out: list[Hypothesis] = []
        for cause, score in ranked[: max(0, k)]:
            out.append(
                Hypothesis(
                    cause=cause,
                    confidence=_score_to_confidence(score),
                    evidence_ids=tuple(self._evidence[cause]),
                )
            )
        return tuple(out)

    def best(self) -> Hypothesis:
        return self.top(k=1)[0]

    # ---- heuristics ----

    def _update_from_metrics(self, *, obs: dict[str, JSONValue], evidence_event_id: str) -> None:
        service = obs.get("service")
        err = obs.get("error_rate")
        lat = obs.get("latency_ms")
        if service == "api" and isinstance(err, (int, float)):
            if float(err) > 0.25:
                self._bump(IncidentType.API_BAD_DEPLOY, amount=2.0, evidence=evidence_event_id)
            elif float(err) > 0.08:
                self._bump(IncidentType.NETWORK_FLAKY, amount=0.8, evidence=evidence_event_id)
        if service == "db" and isinstance(lat, (int, float)):
            if float(lat) > 300.0:
                self._bump(IncidentType.DB_SATURATION, amount=2.0, evidence=evidence_event_id)

        if service == "api" and isinstance(lat, (int, float)) and float(lat) > 300.0:
            # Cascading latency could be DB saturation.
            self._bump(IncidentType.DB_SATURATION, amount=0.6, evidence=evidence_event_id)

    def _update_from_logs(self, *, obs: dict[str, JSONValue], evidence_event_id: str) -> None:
        lines = obs.get("lines")
        if not isinstance(lines, list):
            return
        joined = " ".join([s for s in lines if isinstance(s, str)]).lower()
        if "deploy" in joined and "v2" in joined:
            self._bump(IncidentType.API_BAD_DEPLOY, amount=1.2, evidence=evidence_event_id)
        if "timeout" in joined or "socket" in joined:
            self._bump(IncidentType.NETWORK_FLAKY, amount=1.2, evidence=evidence_event_id)
        if "saturation" in joined or "pool exhausted" in joined:
            self._bump(IncidentType.DB_SATURATION, amount=1.2, evidence=evidence_event_id)

    def _update_from_runbook(self, *, obs: dict[str, JSONValue], evidence_event_id: str) -> None:
        snippets = obs.get("snippets")
        if not isinstance(snippets, list):
            return
        joined = " ".join([s for s in snippets if isinstance(s, str)]).lower()
        if "rollback" in joined:
            self._bump(IncidentType.API_BAD_DEPLOY, amount=0.6, evidence=evidence_event_id)
        if "saturation" in joined:
            self._bump(IncidentType.DB_SATURATION, amount=0.6, evidence=evidence_event_id)
        if "timeout" in joined or "network" in joined:
            self._bump(IncidentType.NETWORK_FLAKY, amount=0.6, evidence=evidence_event_id)

    def _bump(self, cause: IncidentType, *, amount: float, evidence: str) -> None:
        self._score[cause] += amount
        self._evidence[cause].append(evidence)


def _score_to_confidence(score: float) -> ConfidenceLevel:
    if score >= 2.5:
        return ConfidenceLevel.HIGH
    if score >= 1.5:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW
