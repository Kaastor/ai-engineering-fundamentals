from __future__ import annotations

from learning_compiler.types import IncidentType


def incident_for_seed(seed: int) -> IncidentType:
    """Deterministic mapping seed -> incident type.

    Ensures coverage in small eval suites:
    - seeds mod 3 cover all 3 incidents
    - still deterministic / reproducible
    """

    mapping = (
        IncidentType.API_BAD_DEPLOY,
        IncidentType.DB_SATURATION,
        IncidentType.NETWORK_FLAKY,
    )
    return mapping[seed % len(mapping)]
