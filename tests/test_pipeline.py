from pathlib import Path

from business_entity_resolution.pipeline import score_candidate_file


def write_source(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    path.write_text(
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        + "\n".join("\t".join(row) for row in rows)
        + "\n",
        encoding="utf-8",
    )


def test_score_candidate_file_writes_matching_results(tmp_path: Path) -> None:
    source1 = tmp_path / "source1.tsv"
    source2 = tmp_path / "source2.tsv"
    source3 = tmp_path / "source3.tsv"
    candidates = tmp_path / "candidate_pairs.tsv"
    matching = tmp_path / "matching_results.tsv"
    write_source(source1, [("S1-1", "Cafe Lumiere", "12 Main Road", "France"), ("S1-2", "No Match", "", "France")])
    write_source(source2, [("S2-1", "Cafe Lumiere", "12 Main Road", "France"), ("S2-2", "Other", "", "France")])
    write_source(source3, [])
    candidates.write_text(
        "source1_entity_id\tcandidate_entity_ids\nS1-1\tS2-1,S2-2\nS1-2\t\n",
        encoding="utf-8",
    )

    assert score_candidate_file(source1, source2, source3, candidates, matching) == 2
    assert matching.read_text(encoding="utf-8").splitlines() == [
        "source1_entity_id\tmatched_entity_ids",
        "S1-1\tS2-1",
        "S1-2\t",
    ]