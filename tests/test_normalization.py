from business_entity_resolution.normalization import (
    digit_tokens,
    normalize_address,
    normalize_name,
    text_tokens,
)


def test_name_normalization_handles_case_punctuation_and_ampersand() -> None:
    assert normalize_name("A & B, Inc.") == "a and b inc"


def test_address_normalization_preserves_words_and_numbers() -> None:
    assert normalize_address("12-B, Main Road") == "12 b main road"
    assert digit_tokens("12-B, Main Road") == ("12",)


def test_empty_values_are_safe() -> None:
    assert normalize_name(None) == ""
    assert text_tokens("") == ()
