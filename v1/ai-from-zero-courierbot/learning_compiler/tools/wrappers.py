"""Reliability wrappers for tool calls (Meeting 5+).

We implement four reliability primitives:
1) validation,
2) timeouts + retries,
3) idempotency,
4) journaling hooks (provided by the caller).

The wrapper enforces the **tool boundary**:
- allowlist checks live outside the policy,
- tool results are validated before becoming state.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from learning_compiler.core.errors import ToolPermissionError, ToolTimeoutError, ToolValidationError
from learning_compiler.env.grid import GridMap
from learning_compiler.tools.contracts import (
    DoorUnlockRequest,
    ReportDeliveryRequest,
    ToolName,
    ToolRequest,
    ToolResponse,
)
from learning_compiler.tools.simulator import ToolExecutionContext, ToolRawResponse, ToolSimulator
from learning_compiler.tools.validator import ToolParseInfo, validate_tool_response


@dataclass(frozen=True, slots=True)
class ToolCallBudget:
    max_retries_per_call: int


@dataclass(frozen=True, slots=True)
class ToolCallResult:
    raw: ToolRawResponse
    parsed: ToolResponse
    parse_info: ToolParseInfo
    attempts: int
    had_timeout: bool
    had_validation_error: bool


@dataclass(frozen=True, slots=True)
class ToolAllowlist:
    allowed: frozenset[ToolName]

    def require_allowed(self, tool: ToolName) -> None:
        if tool not in self.allowed:
            raise ToolPermissionError(f"tool not allowed in this stage: {tool.value}")


class ReliableToolCaller:
    def __init__(
        self,
        *,
        simulator: ToolSimulator,
        allowlist: ToolAllowlist,
        budget: ToolCallBudget,
    ) -> None:
        self._simulator = simulator
        self._allowlist = allowlist
        self._budget = budget

    def call(
        self,
        request: ToolRequest,
        *,
        call_id: str,
        grid_map: GridMap,
        door_locked: bool,
        delivered: bool,
        ctx: ToolExecutionContext,
        on_attempt: Callable[[int, ToolName], None] | None = None,
        on_warning: Callable[[ToolParseInfo], None] | None = None,
    ) -> ToolCallResult:
        tool = request.tool
        self._allowlist.require_allowed(tool)

        # Idempotency is a *system* concern: fill stable keys here, not in the agent.
        request = _with_idempotency_key(request, call_id=call_id)

        had_timeout = False
        had_validation_error = False

        last_timeout: ToolTimeoutError | None = None
        last_validation: ToolValidationError | None = None

        for attempt in range(self._budget.max_retries_per_call + 1):
            if on_attempt is not None:
                on_attempt(attempt, tool)

            try:
                raw = self._simulator.execute(
                    request,
                    call_id=call_id,
                    attempt=attempt,
                    grid_map=grid_map,
                    door_locked=door_locked,
                    delivered=delivered,
                    ctx=ctx,
                )
            except ToolTimeoutError as e:
                had_timeout = True
                last_timeout = e
                continue

            try:
                parsed, info = validate_tool_response(tool, raw.raw)
            except ToolValidationError as e:
                had_validation_error = True
                last_validation = e
                continue

            if on_warning is not None and info.had_trailing_text:
                on_warning(info)

            return ToolCallResult(
                raw=raw,
                parsed=parsed,
                parse_info=info,
                attempts=attempt + 1,
                had_timeout=had_timeout,
                had_validation_error=had_validation_error,
            )

        # If we exhausted retries, raise the most informative error.
        if last_validation is not None:
            raise last_validation
        if last_timeout is not None:
            raise last_timeout
        raise ToolTimeoutError(f"tool failed after retries: {tool.value}")


def _with_idempotency_key(request: ToolRequest, *, call_id: str) -> ToolRequest:
    # Only side-effectful tools require idempotency.
    if isinstance(request, DoorUnlockRequest):
        if request.idempotency_key is None:
            return DoorUnlockRequest(idempotency_key=f"{call_id}:{ToolName.DOOR_UNLOCK.value}")
        return request
    if isinstance(request, ReportDeliveryRequest):
        if request.idempotency_key is None:
            return ReportDeliveryRequest(idempotency_key=f"{call_id}:{ToolName.REPORT_DELIVERY.value}")
        return request
    return request
