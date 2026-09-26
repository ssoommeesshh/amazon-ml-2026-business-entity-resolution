"""Baseline candidate scoring and match selection."""

from collections.abc import Iterable, Mapping

from .features import baseline_score, pair_features


Record = Mapping[str, str]


def select_matches(
    source1: Record,
    candidates: Iterable[Record],
    threshold: float = 0.80,
) -> list[str]:
    """Return candidate IDs whose baseline pair score reaches ``threshold``."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    scored = []
    for candidate in candidates:
        entity_id = (candidate.get("entity_id") or "").strip()
        if not entity_id:
            raise ValueError("every candidate must have an entity_id")
        score = baseline_score(pair_features(source1, candidate))
        if score >= threshold:
            scored.append((score, entity_id))
    return [entity_id for _, entity_id in sorted(scored, key=lambda item: (-item[0], item[1]))]