"""Challenge metrics for entity-level matching evaluation."""

from collections.abc import Mapping, Iterable


def fbeta_score(predicted: set[str], truth: set[str], beta: float = 0.5) -> float:
    """Compute F-beta for one Source-1 entity, including singleton behavior."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    if not predicted and not truth:
        return 1.0
    if not predicted or not truth:
        return 0.0
    true_positive = len(predicted & truth)
    precision = true_positive / len(predicted)
    recall = true_positive / len(truth)
    denominator = beta * beta * precision + recall
    return (1 + beta * beta) * precision * recall / denominator if denominator else 0.0


def macro_fbeta(
    predictions: Mapping[str, Iterable[str]],
    truth: Mapping[str, Iterable[str]],
    beta: float = 0.5,
) -> float:
    """Compute macro F-beta over every Source-1 entity in the truth mapping."""
    if not truth:
        raise ValueError("truth must contain at least one Source-1 entity")
    scores = []
    for source1_id, true_ids in truth.items():
        predicted_ids = set(predictions.get(source1_id, ()))
        scores.append(fbeta_score(predicted_ids, set(true_ids), beta))
    return sum(scores) / len(scores)