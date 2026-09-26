from business_entity_resolution.features import baseline_score, pair_features


def record(name: str, address: str, country: str = "France") -> dict[str, str]:
    return {"business_name": name, "business_address": address, "country": country}


def test_matching_pair_has_high_similarity_features() -> None:
    features = pair_features(
        record("Cafe Lumiere", "12 Main Road"),
        record("Cafe Lumiere", "12 Main Road"),
    )

    assert features["name_ratio"] == 1.0
    assert features["address_token_overlap"] == 1.0
    assert features["same_country"] == 1.0
    assert baseline_score(features) == 1.0


def test_different_country_is_visible_to_the_score() -> None:
    features = pair_features(
        record("Cafe Lumiere", "12 Main Road", "France"),
        record("Cafe Lumiere", "12 Main Road", "India"),
    )

    assert features["same_country"] == 0.0
    assert baseline_score(features) < 1.0


def test_missing_address_does_not_create_similarity() -> None:
    features = pair_features(record("Cafe Lumiere", ""), record("Cafe Lumiere", "12 Main Road"))

    assert features["address_missing"] == 1.0
    assert features["address_ratio"] == 0.0
    assert features["name_ratio"] == 1.0