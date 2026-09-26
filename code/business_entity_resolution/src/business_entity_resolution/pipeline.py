"""Small end-to-end candidate scoring and submission writing helpers."""

import csv
from pathlib import Path

from .matching import select_matches


def _read_candidate_lists(path: str | Path) -> dict[str, list[str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return {
            row["source1_entity_id"]: [value for value in row["candidate_entity_ids"].split(",") if value]
            for row in csv.DictReader(handle, delimiter="\t")
        }


def _read_records_for_ids(
    paths: tuple[str | Path, ...],
    wanted_ids: set[str],
) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for path in paths:
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                entity_id = row["entity_id"]
                if entity_id in wanted_ids:
                    records[entity_id] = row
    return records


def score_candidate_file(
    source1_path: str | Path,
    source2_path: str | Path,
    source3_path: str | Path,
    candidate_path: str | Path,
    matching_path: str | Path,
    threshold: float = 0.80,
) -> int:
    """Score a candidate TSV and write one matching row per Source-1 row."""
    candidate_lists = _read_candidate_lists(candidate_path)
    source1_records = _read_records_for_ids((source1_path,), set(candidate_lists))
    target_ids = {entity_id for ids in candidate_lists.values() for entity_id in ids}
    target_records = _read_records_for_ids((source2_path, source3_path), target_ids)

    output = Path(matching_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["source1_entity_id", "matched_entity_ids"])
        for source1_id, candidate_ids in candidate_lists.items():
            source1 = source1_records.get(source1_id)
            candidates = [target_records[entity_id] for entity_id in candidate_ids if entity_id in target_records]
            matches = select_matches(source1, candidates, threshold) if source1 else []
            writer.writerow([source1_id, ",".join(matches)])
    return len(candidate_lists)