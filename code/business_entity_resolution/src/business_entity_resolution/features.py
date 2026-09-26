"""Pairwise similarity features and a conservative baseline score."""

from collections.abc import Mapping

from rapidfuzz import fuzz

from .normalization import digit_tokens, normalize_address, normalize_name, text_tokens


Record = Mapping[str, str]


def _overlap(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    """Return overlap over the smaller non-empty token set."""
    left_set, right_set = set(left), set(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / min(len(left_set), len(right_set))


def pair_features(left: Record, right: Record) -> dict[str, float]:
    """Create normalized name, address, digit, and country comparison features."""
    left_name = normalize_name(left.get("business_name"))
    right_name = normalize_name(right.get("business_name"))
    left_address = normalize_address(left.get("business_address"))
    right_address = normalize_address(right.get("business_address"))
    left_name_tokens = text_tokens(left_name)
    right_name_tokens = text_tokens(right_name)
    left_address_tokens = text_tokens(left_address)
    right_address_tokens = text_tokens(right_address)

    return {
        "name_ratio": fuzz.ratio(left_name, right_name) / 100.0 if left_name and right_name else 0.0,
        "name_token_set_ratio": fuzz.token_set_ratio(left_name, right_name) / 100.0 if left_name and right_name else 0.0,
        "name_token_overlap": _overlap(left_name_tokens, right_name_tokens),
        "address_ratio": fuzz.ratio(left_address, right_address) / 100.0 if left_address and right_address else 0.0,
        "address_token_set_ratio": fuzz.token_set_ratio(left_address, right_address) / 100.0 if left_address and right_address else 0.0,
        "address_token_overlap": _overlap(left_address_tokens, right_address_tokens),
        "digit_overlap": _overlap(digit_tokens(left_address), digit_tokens(right_address)),
        "same_country": float((left.get("country") or "").casefold() == (right.get("country") or "").casefold()),
        "name_missing": float(not left_name or not right_name),
        "address_missing": float(not left_address or not right_address),
    }


def baseline_score(features: Mapping[str, float]) -> float:
    """Score a pair with precision-first weights for the initial baseline."""
    score = (
        0.35 * features["name_token_set_ratio"]
        + 0.25 * features["name_ratio"]
        + 0.20 * features["address_token_set_ratio"]
        + 0.10 * features["address_token_overlap"]
        + 0.05 * features["digit_overlap"]
        + 0.05 * features["same_country"]
    )
    return max(0.0, min(1.0, score))