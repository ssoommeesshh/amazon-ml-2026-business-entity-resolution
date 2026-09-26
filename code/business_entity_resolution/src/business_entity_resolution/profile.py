"""Streaming dataset profiling for the entity-resolution challenge."""

import csv
from collections import Counter
from pathlib import Path
from typing import Any


RECORD_COLUMNS = ("entity_id", "business_name", "business_address", "country")


def profile_records(path: str | Path) -> dict[str, Any]:
    """Profile a source TSV without loading it into memory."""
    row_count = 0
    missing = Counter()
    countries = Counter()

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != RECORD_COLUMNS:
            raise ValueError(f"{path} must have columns {list(RECORD_COLUMNS)}")
        for row in reader:
            row_count += 1
            for column in RECORD_COLUMNS:
                if not (row.get(column) or "").strip():
                    missing[column] += 1
            countries[(row.get("country") or "").strip()] += 1

    return {
        "path": str(path),
        "rows": row_count,
        "missing": dict(missing),
        "countries": dict(countries),
    }


def profile_ground_truth(path: str | Path) -> dict[str, Any]:
    """Profile match-list sizes from the training labels."""
    row_count = 0
    empty_count = 0
    match_counts = Counter()

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected = ("source1_entity_id", "matched_entity_ids")
        if tuple(reader.fieldnames or ()) != expected:
            raise ValueError(f"{path} must have columns {list(expected)}")
        for row in reader:
            row_count += 1
            ids = [value for value in (row.get("matched_entity_ids") or "").split(",") if value]
            match_counts[len(ids)] += 1
            empty_count += not ids

    return {
        "path": str(path),
        "rows": row_count,
        "empty_matches": empty_count,
        "match_count_distribution": dict(sorted(match_counts.items())),
    }


def profile_directory(directory: str | Path) -> list[dict[str, Any]]:
    """Profile all source files in a train or test directory."""
    directory = Path(directory)
    reports = []
    for path in sorted(directory.glob("*_source*.tsv")):
        reports.append(profile_records(path))
    ground_truth = directory / "train_ground_truth.tsv"
    if ground_truth.exists():
        reports.append(profile_ground_truth(ground_truth))
    return reports
