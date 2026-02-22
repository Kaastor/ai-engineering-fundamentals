from __future__ import annotations

from dataclasses import dataclass
import random

from learning_compiler.sim.world import SimWorld, WorldConfig
from learning_compiler.types import IncidentType, ScenarioSeed


@dataclass(slots=True, frozen=True)
class ScenarioConfig:
    seed: ScenarioSeed
    incident_override: IncidentType | None = None

    def validate(self) -> None:
        if int(self.seed) < 0:
            raise ValueError("seed must be non-negative")


@dataclass(slots=True, frozen=True)
class Scenario:
    seed: ScenarioSeed
    incident: IncidentType
    world: SimWorld


def generate_scenario(config: ScenarioConfig) -> Scenario:
    config.validate()
    seed_int = int(config.seed)
    rng = random.Random(seed_int ^ 0x5113_2026)  # deterministic but not just "seed"
    incident = config.incident_override or rng.choice(
        [IncidentType.API_BAD_DEPLOY, IncidentType.DB_SATURATION, IncidentType.NETWORK_FLAKY]
    )
    world = SimWorld(WorldConfig(seed=config.seed, incident=incident))
    return Scenario(seed=config.seed, incident=incident, world=world)
