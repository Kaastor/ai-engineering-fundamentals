from __future__ import annotations

from dataclasses import dataclass
import random

from learning_compiler.sim.observations import HealthStatus
from learning_compiler.types import IncidentType, ScenarioSeed, ServiceName


@dataclass(slots=True, frozen=True)
class WorldConfig:
    seed: ScenarioSeed
    incident: IncidentType


@dataclass(slots=True)
class ServiceState:
    version: str
    running: bool


class SimWorld:
    """Deterministic toy 'production' world with two services: api -> db."""

    def __init__(self, config: WorldConfig) -> None:
        self._config = config
        self._rng = random.Random(int(config.seed) ^ 0xBADC0DE)
        self._t = 0
        self._resolved = False
        self._services: dict[ServiceName, ServiceState] = {
            "api": ServiceState(version="v2" if config.incident is IncidentType.API_BAD_DEPLOY else "v1", running=True),
            "db": ServiceState(version="v1", running=True),
        }
        # Snapshot history of *true* metrics (no noise). Used for delayed observations.
        self._history: list[dict[ServiceName, tuple[float, float]]] = []
        self._record_snapshot()

    @property
    def incident(self) -> IncidentType:
        return self._config.incident

    @property
    def time_index(self) -> int:
        return self._t

    @property
    def resolved(self) -> bool:
        return self._resolved

    def tick(self) -> None:
        """Advance simulated time by one step."""

        self._t += 1
        self._record_snapshot()

    # ---- Read APIs (ground truth; tool wrappers add noise/delay) ----

    def true_metrics(self, *, service: ServiceName, delay_steps: int) -> tuple[float, float]:
        idx = max(0, self._t - max(0, delay_steps))
        snap = self._history[idx]
        return snap[service]

    def health(self, *, service: ServiceName) -> tuple[HealthStatus, dict[str, str]]:
        err, lat = self.true_metrics(service=service, delay_steps=0)
        if not self._services[service].running:
            return (HealthStatus.DOWN, {"reason": "process_not_running"})
        if err > 0.60:
            return (HealthStatus.DOWN, {"reason": "error_rate_critical"})
        if err > 0.20 or lat > 400.0:
            return (HealthStatus.DEGRADED, {"reason": "unhealthy_metrics"})
        return (HealthStatus.OK, {"reason": "healthy"})

    def tail_logs(self, *, service: ServiceName, n: int) -> tuple[str, ...]:
        # Logs are deterministic-but-varied based on time and incident.
        base = self._log_templates(service=service)
        lines: list[str] = []
        for _ in range(max(0, n)):
            lines.append(self._rng.choice(base))
        return tuple(lines)

    # ---- Side effects ----

    def restart(self, *, service: ServiceName) -> str:
        self._services[service].running = True
        msg = f"restarted {service}"
        # In this toy world, restart fixes some incidents.
        if not self._resolved:
            if self._config.incident is IncidentType.DB_SATURATION and service == "db":
                self._resolved = True
                msg = "restarted db (cleared saturation)"
            if self._config.incident is IncidentType.NETWORK_FLAKY and service == "api":
                self._resolved = True
                msg = "restarted api (reset connections)"
        self.tick()
        return msg

    def rollback(self, *, service: ServiceName, version: str) -> str:
        self._services[service].version = version
        msg = f"rolled back {service} to {version}"
        if not self._resolved:
            if self._config.incident is IncidentType.API_BAD_DEPLOY and service == "api" and version == "v1":
                self._resolved = True
                msg = "rolled back api to v1 (bad deploy reverted)"
        self.tick()
        return msg

    # ---- Internals ----

    def _record_snapshot(self) -> None:
        self._history.append(
            {
                "api": self._compute_api_metrics(),
                "db": self._compute_db_metrics(),
            }
        )

    def _compute_api_metrics(self) -> tuple[float, float]:
        # Baselines:
        err = 0.01
        lat = 120.0
        if self._resolved:
            return (err, lat)

        if self._config.incident is IncidentType.API_BAD_DEPLOY:
            # Version v2 is "bad": high 5xx + elevated latency.
            if self._services["api"].version == "v2":
                return (0.35, 220.0)
            return (err, lat)
        if self._config.incident is IncidentType.DB_SATURATION:
            # Cascading latency + some timeout errors.
            return (0.05, 420.0)
        if self._config.incident is IncidentType.NETWORK_FLAKY:
            return (0.12, 320.0)
        raise AssertionError("Unhandled incident")

    def _compute_db_metrics(self) -> tuple[float, float]:
        err = 0.005
        lat = 60.0
        if self._resolved:
            return (err, lat)
        if self._config.incident is IncidentType.DB_SATURATION:
            return (0.01, 520.0)
        return (err, lat)

    def _log_templates(self, *, service: ServiceName) -> list[str]:
        if service == "api":
            if self._config.incident is IncidentType.API_BAD_DEPLOY and not self._resolved:
                return [
                    "ERROR 5xx spike detected after deploy v2",
                    "stacktrace: NullPointerException in handler /checkout",
                    "INFO request_id=abc123 latency_ms=480",
                    "WARN retry exhausted talking to db",
                ]
            if self._config.incident is IncidentType.DB_SATURATION and not self._resolved:
                return [
                    "WARN upstream db latency high; request slow",
                    "INFO request_id=def456 latency_ms=610",
                    "ERROR timeout when calling db",
                    "INFO circuit_breaker=open",
                ]
            if self._config.incident is IncidentType.NETWORK_FLAKY and not self._resolved:
                return [
                    "ERROR timeout when calling db (network)",
                    "WARN socket hang up; retrying",
                    "INFO request_id=ghi789 latency_ms=350",
                    "WARN retry budget exceeded",
                ]
            return [
                "INFO api serving traffic normally",
                "INFO request_id=ok123 latency_ms=110",
                "INFO healthcheck passed",
            ]
        # db
        if self._config.incident is IncidentType.DB_SATURATION and not self._resolved:
            return [
                "WARN queue depth high; saturation suspected",
                "INFO slow query detected latency_ms=900",
                "WARN connection pool exhausted",
                "INFO vacuum started",
            ]
        return [
            "INFO db healthy",
            "INFO checkpoint complete",
            "INFO connections=42",
        ]
