"""Disk-backed baseline candidate generation using DuckDB."""

from pathlib import Path

import duckdb


NORMALIZED = """
lower(
  regexp_replace(
    replace(coalesce({column}, ''), '&', ' and '),
    '[^[:alnum:][:space:]]', ' ', 'g'
  )
)
"""


def _read_source(connection: duckdb.DuckDBPyConnection, path: str | Path, alias: str) -> None:
    """Register one TSV source as a DuckDB view with normalized fields."""
    escaped = str(path).replace("'", "''")
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW {alias} AS
        SELECT
          entity_id,
          country,
          trim(regexp_replace({NORMALIZED.format(column='business_name')}, '\\s+', ' ', 'g')) AS name_norm,
          trim(regexp_replace({NORMALIZED.format(column='business_address')}, '\\s+', ' ', 'g')) AS address_norm
        FROM read_csv('{escaped}', delim='\\t', header=true, nullstr='')
        """
    )


def generate_exact_candidates(
    source1_path: str | Path,
    source2_path: str | Path,
    source3_path: str | Path,
    output_path: str | Path,
    max_candidates: int = 500,
) -> int:
    """Generate bounded exact-name/address candidates and return row count."""
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect()
    try:
        _read_source(connection, source1_path, "source1")
        _read_source(connection, source2_path, "source2")
        _read_source(connection, source3_path, "source3")
        connection.execute(
            """
            CREATE OR REPLACE TEMP VIEW targets AS
            SELECT * FROM source2
            UNION ALL
            SELECT * FROM source3
            """
        )
        query = f"""
        COPY (
          WITH matched AS (
            SELECT
              source1.entity_id AS source1_entity_id,
              target.entity_id AS candidate_entity_id,
              row_number() OVER (
                PARTITION BY source1.entity_id ORDER BY target.entity_id
              ) AS candidate_rank
            FROM source1
            JOIN targets AS target
              ON source1.country = target.country
             AND (
               (source1.name_norm <> '' AND source1.name_norm = target.name_norm)
               OR
               (source1.address_norm <> '' AND source1.address_norm = target.address_norm)
             )
          ), candidate_lists AS (
            SELECT
              source1_entity_id,
              string_agg(candidate_entity_id, ',' ORDER BY candidate_entity_id) AS candidate_entity_ids
            FROM matched
            WHERE candidate_rank <= {max_candidates}
            GROUP BY source1_entity_id
          )
          SELECT
            source1.entity_id AS source1_entity_id,
            coalesce(candidate_lists.candidate_entity_ids, '') AS candidate_entity_ids
          FROM source1
          LEFT JOIN candidate_lists
            ON source1.entity_id = candidate_lists.source1_entity_id
          ORDER BY source1.entity_id
        ) TO '{str(output).replace("'", "''")}'
        (FORMAT CSV, DELIMITER '\\t', HEADER, QUOTE '')
        """
        connection.execute(query)
        return int(connection.execute(f"SELECT count(*) FROM read_csv('{str(output).replace(chr(39), chr(39) + chr(39))}', delim='\\t', header=true)").fetchone()[0])
    finally:
        connection.close()