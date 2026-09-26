"""Conservative text normalization for business names and addresses."""

import re
import unicodedata


NON_ALNUM = re.compile(r"[^\w\s]", re.UNICODE)
WHITESPACE = re.compile(r"\s+")
ADDRESS_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def normalize_text(value: str | None) -> str:
    """Normalize Unicode, case, punctuation, and whitespace."""
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    text = text.replace("&", " and ")
    text = NON_ALNUM.sub(" ", text)
    return WHITESPACE.sub(" ", text).strip()


def normalize_name(value: str | None) -> str:
    """Return a normalized business name without removing legal suffixes."""
    return normalize_text(value)


def normalize_address(value: str | None) -> str:
    """Return a normalized address while preserving address tokens and digits."""
    return normalize_text(value)


def text_tokens(value: str | None) -> tuple[str, ...]:
    """Return stable normalized tokens for set-based blocking features."""
    normalized = normalize_text(value)
    if not normalized:
        return ()
    return tuple(ADDRESS_TOKEN_RE.findall(normalized))


def digit_tokens(value: str | None) -> tuple[str, ...]:
    """Return numeric token strings, useful for postal and street-number overlap."""
    return tuple(token for token in text_tokens(value) if token.isdigit())