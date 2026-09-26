"""Small, reusable I/O helpers for the challenge pipeline."""

from pathlib import Path
from typing import Iterable

import pandas as pd


RECORD_COLUMNS = ["entity_id", "business_name", "business_address", "country"]


def read_records(path: str | Path) -> pd.DataFrame:
    """Read one challenge record TSV with the required schema."""
    frame = pd.read_csv(path, sep="\t", dtype="string", keep_default_na=False)
    missing = [column for column in RECORD_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")
    return frame[RECORD_COLUMNS]


def write_id_lists(
    path: str | Path,
    source1_ids: Iterable[str],
    id_lists: Iterable[Iterable[str]],
    list_column: str,
) -> None:
    """Write one output row per Source-1 ID using tab-separated fields."""
    rows = []
    for source1_id, ids in zip(source1_ids, id_lists):
        unique_ids = list(dict.fromkeys(str(entity_id) for entity_id in ids))
        rows.append({
            "source1_entity_id": str(source1_id),
            list_column: ",".join(unique_ids),
        })
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, sep="\t", index=False)
