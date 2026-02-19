from __future__ import annotations

from learning_compiler.env.types import Direction
from learning_compiler.learning.knn import KnnConfig, train_knn


def test_knn_predicts_majority_vote() -> None:
    vectors = [
        (1, 0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0, 0),
        (0, 1, 0, 0, 0, 0),
    ]
    labels = [Direction.EAST, Direction.EAST, Direction.EAST, Direction.SOUTH]
    model = train_knn(vectors=vectors, labels=labels, config=KnnConfig(k=3))
    assert model.predict((1, 0, 0, 0, 0, 0)) == Direction.EAST
