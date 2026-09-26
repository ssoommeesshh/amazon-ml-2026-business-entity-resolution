import pytest

from business_entity_resolution.metrics import fbeta_score, macro_fbeta


def test_singleton_cases_are_scored_correctly() -> None:
    assert fbeta_score(set(), set()) == 1.0
    assert fbeta_score({"S2-1"}, set()) == 0.0
    assert fbeta_score(set(), {"S2-1"}) == 0.0


def test_fbeta_weights_false_positive_against_precision() -> None:
    score = fbeta_score({"S2-1", "S2-2"}, {"S2-1"})
    assert score == pytest.approx(0.5555555556)


def test_macro_fbeta_includes_all_truth_entities() -> None:
    predictions = {"S1-1": {"S2-1"}}
    truth = {"S1-1": {"S2-1"}, "S1-2": set()}

    assert macro_fbeta(predictions, truth) == 1.0