from pathlib import Path

import pandas as pd

from business_entity_resolution.io import read_records, write_id_lists


def test_read_records_uses_tsv_schema(tmp_path: Path) -> None:
    source = tmp_path / "records.tsv"
    pd.DataFrame([
        {
            "entity_id": "S1-1",
            "business_name": "Example",
            "business_address": "Address",
            "country": "France",
        }
    ]).to_csv(source, sep="\t", index=False)

    result = read_records(source)

    assert list(result.columns) == ["entity_id", "business_name", "business_address", "country"]
    assert result.iloc[0]["country"] == "France"


def test_write_id_lists_deduplicates_ids_and_uses_tabs(tmp_path: Path) -> None:
    destination = tmp_path / "output.tsv"
    write_id_lists(destination, ["S1-1"], [["S2-1", "S2-1", "S3-1"]], "matched_entity_ids")

    text = destination.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "source1_entity_id\tmatched_entity_ids"
    assert "S1-1\tS2-1,S3-1" in text
