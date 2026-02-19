from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Generic, Hashable, Iterable, Mapping, Sequence, TypeVar


LabelT = TypeVar("LabelT", bound=Hashable)


@dataclass(frozen=True, slots=True)
class Example(Generic[LabelT]):
    features: tuple[float, ...]
    label: LabelT


@dataclass(frozen=True, slots=True)
class KnnClassifier(Generic[LabelT]):
    """A tiny k-NN classifier (math-light, code-first).

    - 'Training' is just storing examples.
    - Prediction uses majority vote among k nearest points.

    This is not meant to be fast. It is meant to be readable.
    """

    k: int
    examples: tuple[Example[LabelT], ...]

    @staticmethod
    def fit(*, k: int, examples: Sequence[Example[LabelT]]) -> KnnClassifier[LabelT]:
        if k <= 0:
            raise ValueError("k must be >= 1")
        if not examples:
            raise ValueError("Need at least one example")
        return KnnClassifier(k=k, examples=tuple(examples))

    def predict(self, features: tuple[float, ...]) -> LabelT:
        scored: list[tuple[float, Example[LabelT]]] = []
        for ex in self.examples:
            d2 = _dist2(features, ex.features)
            scored.append((d2, ex))

        scored.sort(key=lambda t: t[0])
        k_nearest = scored[: min(self.k, len(scored))]

        votes: dict[LabelT, int] = {}
        for _d2, ex in k_nearest:
            votes[ex.label] = votes.get(ex.label, 0) + 1

        # Deterministic tie-breaker: sort by (vote desc, repr(label) asc).
        winners = sorted(votes.items(), key=lambda kv: (-kv[1], repr(kv[0])))
        return winners[0][0]


def accuracy(*, model: KnnClassifier[LabelT], data: Iterable[Example[LabelT]]) -> float:
    total = 0
    correct = 0
    for ex in data:
        total += 1
        if model.predict(ex.features) == ex.label:
            correct += 1
    if total == 0:
        raise ValueError("Empty dataset")
    return correct / total


def make_blob_dataset(
    *,
    rng: random.Random,
    n_per_class: int,
    centers: Mapping[LabelT, tuple[float, float]],
    std: float = 1.0,
) -> list[Example[LabelT]]:
    """Generate a simple 2D dataset (Gaussian blobs) for teaching.

    No numpy required; uses rng.gauss for determinism via seed.
    """

    if n_per_class <= 0:
        raise ValueError("n_per_class must be > 0")
    if std <= 0.0:
        raise ValueError("std must be > 0")

    dataset: list[Example[LabelT]] = []
    for label, (cx, cy) in centers.items():
        for _ in range(n_per_class):
            x = rng.gauss(cx, std)
            y = rng.gauss(cy, std)
            dataset.append(Example(features=(x, y), label=label))
    rng.shuffle(dataset)
    return dataset


def _dist2(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError("Feature vectors must have same dimensionality")
    return sum((ai - bi) ** 2 for ai, bi in zip(a, b, strict=True))
