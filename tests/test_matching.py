import pytest

from business_entity_resolution.matching import select_matches


def record(entity_id: str, name: str, address: str, country: str = "France") -> dict[str, str]:
    return {
        "entity_id": entity_id,
        "business_name": name,
        "business_address": address,
        "country": country,
    }


def test_matching_selects_multiple_strong_candidates() -> None:
    source1 = record("S1-1", "Cafe Lumiere", "12 Main Road")
    candidates = [
        record("S2-1", "Cafe Lumiere", "12 Main Road"),
        record("S3-1", "Cafe Lumiere", "12 Main Road"),
        record("S2-2", "Different Shop", "99 Other Street"),
    ]

    assert select_matches(source1, candidates, threshold=0.80) == ["S2-1", "S3-1"]


def test_matching_can_return_a_singleton() -> None:
    source1 = record("S1-1", "Cafe Lumiere", "12 Main Road")
    assert select_matches(source1, [record("S2-1", "Unrelated", "")], threshold=0.95) == []


def test_threshold_is_validated() -> None:
    with pytest.raises(ValueError):
        select_matches(record("S1-1", "A", "B"), [], threshold=1.1)