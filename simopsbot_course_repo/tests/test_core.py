from __future__ import annotations

from pathlib import Path

import pytest

from learning_compiler.agent.loop import run_agent
from learning_compiler.agent.policy import Policy, PolicyDecision
from learning_compiler.agent.state import AgentProfile, AgentRunConfig
from learning_compiler.agent.actions import ActRollback
from learning_compiler.agent.validator import ActionValidationError, parse_action_proposal
from learning_compiler.types import IncidentType


def test_action_validator_parses_valid_restart() -> None:
    action = parse_action_proposal('{"type":"ACT_RESTART","service":"api"}')
    assert action.type.value == "ACT_RESTART"


def test_action_validator_rejects_non_json() -> None:
    with pytest.raises(ActionValidationError):
        _ = parse_action_proposal("restart everything please")


def test_policy_blocks_db_rollback() -> None:
    policy = Policy()
    outcome = policy.evaluate(
        action=ActRollback(service="db", version="v2"),
        side_effect_actions_so_far=0,
        max_side_effect_actions=3,
        best_hypothesis=None,
        have_any_metrics=True,
    )
    assert outcome.decision is PolicyDecision.BLOCK


def test_run_is_deterministic(tmp_path: Path) -> None:
    cfg = AgentRunConfig(seed=7, profile=AgentProfile.WEEK5)

    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    r1 = run_agent(config=cfg, out_dir=out_a, incident_override=IncidentType.API_BAD_DEPLOY)
    r2 = run_agent(config=cfg, out_dir=out_b, incident_override=IncidentType.API_BAD_DEPLOY)

    j1 = Path(r1.journal_path).read_text(encoding="utf-8")
    j2 = Path(r2.journal_path).read_text(encoding="utf-8")
    assert j1 == j2
