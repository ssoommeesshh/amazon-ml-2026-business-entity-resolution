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


def test_unicode_compatibility_and_whitespace_are_normalized() -> None:
    assert normalize_name("  Ｃａｆｅ\u00a0Müller  ") == "cafe müller"


def test_non_ascii_letters_are_preserved() -> None:
    assert normalize_name("École Française") == "école française"
    assert text_tokens("École Française") == ("école", "française")


def test_token_order_and_legal_suffix_are_preserved() -> None:
    assert normalize_name("Prime Money Ltd") == "prime money ltd"
    assert text_tokens("Money Prime") != text_tokens("Prime Money")
