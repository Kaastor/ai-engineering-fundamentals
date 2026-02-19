from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Generic, Mapping, Sequence, TypeVar


HypothesisT = TypeVar("HypothesisT")


@dataclass(frozen=True, slots=True)
class DiscreteDistribution(Generic[HypothesisT]):
    """A small immutable discrete probability distribution.

    Internally stored as a sorted tuple for determinism and safe hashing.
    """

    items: tuple[tuple[HypothesisT, float], ...]

    def support(self) -> Sequence[HypothesisT]:
        return [h for h, _p in self.items]

    def prob(self, hypothesis: HypothesisT) -> float:
        for h, p in self.items:
            if h == hypothesis:
                return p
        return 0.0

    def as_dict(self) -> dict[HypothesisT, float]:
        return {h: p for h, p in self.items}

    def entropy_bits(self) -> float:
        """Shannon entropy in bits (math-light but useful intuition)."""

        total = 0.0
        for _h, p in self.items:
            if p <= 0.0:
                continue
            total -= p * log2(p)
        return total


def normalize(probs: Mapping[HypothesisT, float]) -> DiscreteDistribution[HypothesisT]:
    total = sum(probs.values())
    if total <= 0.0:
        raise ValueError("Cannot normalize: total probability mass must be > 0")

    normalized_items = ((h, p / total) for h, p in probs.items())
    items = tuple(sorted(normalized_items, key=lambda kv: repr(kv[0])))
    return DiscreteDistribution(items=items)


def bayes_update(
    *,
    prior: DiscreteDistribution[HypothesisT],
    likelihood: Mapping[HypothesisT, float],
) -> DiscreteDistribution[HypothesisT]:
    """Bayesian update: posterior(h) ∝ prior(h) * likelihood(h).

    The caller provides likelihood(h) = P(evidence | hypothesis=h) for hypotheses
    in the prior support.
    """

    unnorm: dict[HypothesisT, float] = {}
    for h, p in prior.items:
        lh = likelihood.get(h)
        if lh is None:
            raise KeyError(f"Missing likelihood for hypothesis {h!r}")
        unnorm[h] = p * lh
    return normalize(unnorm)
