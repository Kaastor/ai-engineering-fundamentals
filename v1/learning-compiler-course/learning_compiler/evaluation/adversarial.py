from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.agent.loop import ActionMediator, MediationResult
from learning_compiler.agent.types import Action, ActionKind, EffectType, Intent


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    """A deliberately small 'system policy' for teaching.

    The important lesson is architectural:
    - policies live outside the model
    - policies are deterministic and testable
    """

    allowed_tool_names: frozenset[str]
    max_write_actions: int = 1
    max_charge_cents: int = 2_500  # e.g., $25.00


class AllowlistMediator(ActionMediator):
    def __init__(self, *, policy: SecurityPolicy) -> None:
        self._policy = policy

    def mediate(self, *, intent: Intent, action: Action, step_index: int) -> MediationResult:
        # Action kind gating.
        if action.kind == ActionKind.TOOL and action.name not in self._policy.allowed_tool_names:
            return MediationResult(allowed=False, reason=f"tool '{action.name}' not allowlisted")

        # Crude effect gating.
        if action.effect == EffectType.WRITE and intent.budget.max_side_effects > self._policy.max_write_actions:
            return MediationResult(allowed=False, reason="intent requests too many side effects for this demo policy")

        # Domain-specific example: charging a card.
        if action.name == "charge_card":
            amount_raw = action.param("amount_cents")
            if amount_raw is None:
                return MediationResult(allowed=False, reason="missing amount_cents parameter")
            try:
                amount = int(amount_raw)
            except ValueError:
                return MediationResult(allowed=False, reason="amount_cents must be an int")
            if amount > self._policy.max_charge_cents:
                return MediationResult(allowed=False, reason=f"amount {amount} exceeds max_charge_cents")

        return MediationResult(allowed=True, reason="allowed")
