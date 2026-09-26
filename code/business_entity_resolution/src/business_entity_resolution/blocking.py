"""Candidate generation using conservative, country-aware blocking keys."""

from collections import defaultdict
from typing import Iterable, Mapping

from .normalization import digit_tokens, normalize_address, normalize_name, text_tokens


Record = Mapping[str, str]


def blocking_keys(record: Record, min_token_length: int = 4) -> tuple[str, ...]:
    """Return exact blocking keys for one source record.

    Keys include the country so records from different countries cannot block
    together. Short/common words are excluded from token blocks to limit noise.
    """
    country = (record.get("country") or "").strip().casefold()
    name = normalize_name(record.get("business_name"))
    address = normalize_address(record.get("business_address"))
    keys: set[str] = set()

    if name:
        keys.add(f"{country}|name|{name}")
    for token in text_tokens(name):
        if len(token) >= min_token_length:
            keys.add(f"{country}|name_token|{token}")
    for token in text_tokens(address):
        if len(token) >= min_token_length:
            keys.add(f"{country}|address_token|{token}")
    for token in digit_tokens(address):
        keys.add(f"{country}|address_digit|{token}")
    return tuple(sorted(keys))


class CandidateIndex:
    """In-memory block index for sampled data and bounded local experiments."""

    def __init__(self, max_bucket_size: int = 500) -> None:
        if max_bucket_size < 1:
            raise ValueError("max_bucket_size must be positive")
        self.max_bucket_size = max_bucket_size
        self._blocks: dict[str, set[str]] = defaultdict(set)
        self._overflow: set[str] = set()

    def add(self, record: Record) -> None:
        """Add one S2/S3 record unless one of its blocks is already too broad."""
        entity_id = (record.get("entity_id") or "").strip()
        if not entity_id:
            raise ValueError("record must contain a non-empty entity_id")
        for key in blocking_keys(record):
            if key in self._overflow:
                continue
            bucket = self._blocks[key]
            if entity_id in bucket:
                continue
            if len(bucket) >= self.max_bucket_size:
                self._overflow.add(key)
                del self._blocks[key]
                continue
            bucket.add(entity_id)

    def add_many(self, records: Iterable[Record]) -> None:
        for record in records:
            self.add(record)

    def candidates(self, record: Record) -> set[str]:
        """Return the union of IDs sharing at least one non-overflow block."""
        result: set[str] = set()
        for key in blocking_keys(record):
            result.update(self._blocks.get(key, ()))
        return result

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    @property
    def overflow_count(self) -> int:
        return len(self._overflow)