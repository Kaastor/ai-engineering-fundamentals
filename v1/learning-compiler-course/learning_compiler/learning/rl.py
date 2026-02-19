from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from learning_compiler.planning.gridworld import GridPos, GridWorld, Move


@dataclass(frozen=True, slots=True)
class Transition:
    next_state: GridPos
    reward: float
    done: bool


@dataclass(frozen=True, slots=True)
class QLearningResult:
    q_values: Mapping[tuple[GridPos, Move], float]
    policy: Mapping[GridPos, Move]
    episodes: int


class GridWorldMDP:
    """A tiny deterministic MDP for tabular Q-learning demos."""

    def __init__(
        self,
        *,
        world: GridWorld,
        step_reward: float = -1.0,
        goal_reward: float = 10.0,
    ) -> None:
        self._world = world
        self._step_reward = step_reward
        self._goal_reward = goal_reward

    @property
    def start(self) -> GridPos:
        return self._world.start

    @property
    def goal(self) -> GridPos:
        return self._world.goal

    def actions(self, state: GridPos) -> tuple[Move, ...]:
        # Reuse deterministic action order from GridWorld.
        return tuple(self._world.as_problem().actions(state))

    def step(self, *, state: GridPos, action: Move) -> Transition:
        nxt = self._world.as_problem().result(state, action)
        if nxt == self.goal:
            return Transition(next_state=nxt, reward=self._goal_reward, done=True)
        return Transition(next_state=nxt, reward=self._step_reward, done=False)


def q_learning(
    *,
    mdp: GridWorldMDP,
    rng: random.Random,
    episodes: int,
    alpha: float = 0.5,
    gamma: float = 0.95,
    epsilon: float = 0.2,
    max_steps_per_episode: int = 200,
) -> QLearningResult:
    if episodes <= 0:
        raise ValueError("episodes must be > 0")
    if not (0.0 < alpha <= 1.0):
        raise ValueError("alpha must be in (0, 1]")
    if not (0.0 <= gamma <= 1.0):
        raise ValueError("gamma must be in [0, 1]")
    if not (0.0 <= epsilon <= 1.0):
        raise ValueError("epsilon must be in [0, 1]")

    q: dict[tuple[GridPos, Move], float] = {}

    def q_value(s: GridPos, a: Move) -> float:
        return q.get((s, a), 0.0)

    for _episode in range(episodes):
        state = mdp.start
        for _t in range(max_steps_per_episode):
            actions = mdp.actions(state)
            if not actions:
                break

            action = _epsilon_greedy_action(
                rng=rng,
                state=state,
                actions=actions,
                q=q_value,
                epsilon=epsilon,
            )
            trans = mdp.step(state=state, action=action)

            next_actions = mdp.actions(trans.next_state)
            best_next = 0.0 if trans.done or not next_actions else max(q_value(trans.next_state, a) for a in next_actions)

            old = q_value(state, action)
            target = trans.reward + gamma * best_next
            q[(state, action)] = (1 - alpha) * old + alpha * target

            state = trans.next_state
            if trans.done:
                break

    policy: dict[GridPos, Move] = {}
    # Build a greedy policy over states we have seen in Q-table.
    seen_states = {s for (s, _a) in q.keys()}
    for s in seen_states:
        actions = mdp.actions(s)
        if not actions:
            continue
        policy[s] = _greedy_action(state=s, actions=actions, q=q_value)

    return QLearningResult(q_values=q, policy=policy, episodes=episodes)


def _epsilon_greedy_action(
    *,
    rng: random.Random,
    state: GridPos,
    actions: tuple[Move, ...],
    q: Callable[[GridPos, Move], float],
    epsilon: float,
) -> Move:
    if rng.random() < epsilon:
        return actions[rng.randrange(len(actions))]
    return _greedy_action(state=state, actions=actions, q=q)


def _greedy_action(
    *,
    state: GridPos,
    actions: tuple[Move, ...],
    q: Callable[[GridPos, Move], float],
) -> Move:
    # Deterministic tie-breaker: (value desc, repr(action) asc).
    scored = [(q(state, a), a) for a in actions]
    scored.sort(key=lambda va: (-va[0], repr(va[1])))
    return scored[0][1]
