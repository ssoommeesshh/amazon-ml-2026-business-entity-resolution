from pathlib import Path

from business_entity_resolution.duckdb_candidates import generate_exact_candidates


def write_source(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    path.write_text(
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        + "\n".join("\t".join(row) for row in rows)
        + "\n",
        encoding="utf-8",
    )


def test_generate_exact_candidates_writes_one_row_per_matching_s1(tmp_path: Path) -> None:
    source1 = tmp_path / "source1.tsv"
    source2 = tmp_path / "source2.tsv"
    source3 = tmp_path / "source3.tsv"
    output = tmp_path / "candidate_pairs.tsv"
    write_source(source1, [("S1-1", "Cafe Lumiere", "12 Main Road", "France"), ("S1-2", "No Match", "", "France")])
    write_source(source2, [("S2-1", "Cafe Lumiere", "99 Other Street", "France")])
    write_source(source3, [("S3-1", "Other Shop", "12 Main Road", "France")])

    assert generate_exact_candidates(source1, source2, source3, output) == 2
    assert output.read_text(encoding="utf-8").splitlines() == [
        "source1_entity_id\tcandidate_entity_ids",
        "S1-1\tS2-1,S3-1",
        "S1-2\t",
    ]


def test_sample_rows_limits_each_input_source(tmp_path: Path) -> None:
    source1 = tmp_path / "source1.tsv"
    source2 = tmp_path / "source2.tsv"
    source3 = tmp_path / "source3.tsv"
    output = tmp_path / "candidate_pairs.tsv"
    write_source(source1, [("S1-1", "Cafe Lumiere", "12 Main Road", "France"), ("S1-2", "Extra", "", "France")])
    write_source(source2, [("S2-1", "Cafe Lumiere", "", "France"), ("S2-2", "Cafe Lumiere", "", "France")])
    write_source(source3, [("S3-1", "Cafe Lumiere", "", "France")])

    assert generate_exact_candidates(source1, source2, source3, output, sample_rows=1) == 1
    assert output.read_text(encoding="utf-8").splitlines() == [
        "source1_entity_id\tcandidate_entity_ids",
        "S1-1\tS2-1,S3-1",
    ]


def test_source1_and_target_limits_are_independent(tmp_path: Path) -> None:
    source1 = tmp_path / "source1.tsv"
    source2 = tmp_path / "source2.tsv"
    source3 = tmp_path / "source3.tsv"
    output = tmp_path / "candidate_pairs.tsv"
    write_source(source1, [("S1-1", "Cafe Lumiere", "", "France"), ("S1-2", "Other", "", "France")])
    write_source(source2, [("S2-1", "Cafe Lumiere", "", "France"), ("S2-2", "Cafe Lumiere", "", "France")])
    write_source(source3, [("S3-1", "Cafe Lumiere", "", "France")])

    assert generate_exact_candidates(
        source1, source2, source3, output, source1_sample_rows=1, target_sample_rows=None
    ) == 1
    assert output.read_text(encoding="utf-8").splitlines() == [
        "source1_entity_id\tcandidate_entity_ids",
        "S1-1\tS2-1,S2-2,S3-1",
    ]