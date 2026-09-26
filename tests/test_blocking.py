from business_entity_resolution.blocking import CandidateIndex, blocking_keys


def record(entity_id: str, name: str, address: str, country: str = "France") -> dict[str, str]:
    return {
        "entity_id": entity_id,
        "business_name": name,
        "business_address": address,
        "country": country,
    }


def test_keys_are_country_aware_and_include_exact_name() -> None:
    keys = blocking_keys(record("S2-1", "Cafe Lumiere", "12 Main Road"))

    assert "france|name|cafe lumiere" in keys
    assert "france|name_token|lumiere" in keys
    assert all(key.startswith("france|") for key in keys)


def test_index_retrieves_name_and_address_candidates() -> None:
    index = CandidateIndex()
    index.add_many([
        record("S2-1", "Cafe Lumiere", "12 Main Road"),
        record("S3-1", "Different Shop", "12 Main Road"),
        record("S2-2", "Cafe Lumiere", "99 Other Street", "India"),
    ])

    candidates = index.candidates(record("S1-1", "Cafe Lumiere", "12 Main Road"))

    assert candidates == {"S2-1", "S3-1"}


def test_common_block_overflow_is_excluded() -> None:
    index = CandidateIndex(max_bucket_size=2)
    index.add_many([
        record("S2-1", "Alpha Market", "1 Road"),
        record("S2-2", "Beta Market", "2 Road"),
        record("S2-3", "Gamma Market", "3 Road"),
    ])

    assert index.candidates(record("S1-1", "Other Market", "99 Road")) == set()
    assert index.overflow_count > 0


def test_empty_fields_do_not_create_global_keys() -> None:
    keys = blocking_keys(record("S2-1", "", "", "France"))

    assert keys == ()