"""A tiny k-nearest neighbors policy model.

We implement kNN from scratch to avoid heavy dependencies and to keep the learning mechanism transparent.
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from learning_compiler.env.types import Direction


@dataclass(frozen=True, slots=True)
class KnnConfig:
    k: int = 7

    def __post_init__(self) -> None:
        if self.k <= 0:
            raise ValueError("k must be positive")


@dataclass(frozen=True, slots=True)
class KnnModel:
    config: KnnConfig
    vectors: tuple[tuple[int, int, int, int, int, int], ...]
    labels: tuple[Direction, ...]

    def __post_init__(self) -> None:
        if len(self.vectors) != len(self.labels):
            raise ValueError("vectors and labels must have equal length")
        if not self.vectors:
            raise ValueError("empty training set")

    def predict(self, vector: tuple[int, int, int, int, int, int]) -> Direction:
        # Compute distances to all points (explicit loops are fine at this scale).
        scored: list[tuple[int, Direction]] = []
        for v, label in zip(self.vectors, self.labels, strict=True):
            scored.append((_l1_distance(v, vector), label))
        scored.sort(key=lambda t: t[0])

        k = min(self.config.k, len(scored))
        votes: dict[Direction, int] = {}
        for dist, label in scored[:k]:
            _ = dist
            votes[label] = votes.get(label, 0) + 1

        # Deterministic tie-break by fixed direction order.
        best = max(votes.values())
        for d in Direction.all():
            if votes.get(d, 0) == best:
                return d
        # Should be unreachable.
        return scored[0][1]

    def save(self, path: Path) -> None:
        obj = {
            "k": self.config.k,
            "vectors": [list(v) for v in self.vectors],
            "labels": [lbl.value for lbl in self.labels],
        }
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> KnnModel:
        # JSON is an untyped boundary; validate aggressively here.
        raw: object = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("model file must contain a JSON object")

        k_raw = raw.get("k")
        vectors_raw = raw.get("vectors")
        labels_raw = raw.get("labels")

        if not isinstance(k_raw, int):
            raise ValueError("model file: 'k' must be an integer")
        k = k_raw

        if not isinstance(vectors_raw, list):
            raise ValueError("model file: 'vectors' must be a list")
        if not isinstance(labels_raw, list):
            raise ValueError("model file: 'labels' must be a list")

        vectors = tuple(_parse_vector(row) for row in vectors_raw)
        labels = tuple(Direction(str(lbl)) for lbl in labels_raw)
        return KnnModel(config=KnnConfig(k=k), vectors=vectors, labels=labels)




def _parse_vector(row: object) -> tuple[int, int, int, int, int, int]:
    if not isinstance(row, list) or len(row) != 6:
        raise ValueError("vector must be a list of length 6")
    vals = [int(x) for x in row]
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])

def train_knn(*, vectors: Iterable[tuple[int, int, int, int, int, int]], labels: Iterable[Direction], config: KnnConfig) -> KnnModel:
    vec_t = tuple(vectors)
    lbl_t = tuple(labels)
    return KnnModel(config=config, vectors=vec_t, labels=lbl_t)


def _l1_distance(a: tuple[int, int, int, int, int, int], b: tuple[int, int, int, int, int, int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b, strict=True))
