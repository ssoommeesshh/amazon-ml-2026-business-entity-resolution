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


def _read_source(
  connection: duckdb.DuckDBPyConnection,
  path: str | Path,
  alias: str,
  sample_rows: int | None = None,
) -> None:
    """Register one TSV source as a DuckDB view with normalized fields."""
    escaped = str(path).replace("'", "''")
    limit = "" if sample_rows is None else f" LIMIT {sample_rows}"
    connection.execute(
      f"""
        CREATE OR REPLACE VIEW {alias} AS
        SELECT
          entity_id,
          country,
          trim(regexp_replace({NORMALIZED.format(column='business_name')}, '\\s+', ' ', 'g')) AS name_norm,
          trim(regexp_replace({NORMALIZED.format(column='business_address')}, '\\s+', ' ', 'g')) AS address_norm
        FROM read_csv('{escaped}', delim='\\t', header=true, nullstr=''){limit}
        """
    )


def generate_exact_candidates(
    source1_path: str | Path,
    source2_path: str | Path,
    source3_path: str | Path,
    output_path: str | Path,
    max_candidates: int = 500,
    sample_rows: int | None = None,
    source1_sample_rows: int | None = None,
    target_sample_rows: int | None = None,
    max_token_frequency: int = 5000,
) -> int:
    """Generate bounded exact-name/address candidates and return row count."""
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")
    if max_token_frequency < 1:
      raise ValueError("max_token_frequency must be positive")
    if sample_rows is not None and sample_rows < 1:
      raise ValueError("sample_rows must be positive when provided")
    source1_sample_rows = source1_sample_rows or sample_rows
    target_sample_rows = target_sample_rows or sample_rows
    if source1_sample_rows is not None and source1_sample_rows < 1:
      raise ValueError("source1_sample_rows must be positive when provided")
    if target_sample_rows is not None and target_sample_rows < 1:
      raise ValueError("target_sample_rows must be positive when provided")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect()
    try:
        _read_source(connection, source1_path, "source1", source1_sample_rows)
        _read_source(connection, source2_path, "source2", target_sample_rows)
        _read_source(connection, source3_path, "source3", target_sample_rows)
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
          WITH target_tokens AS (
            SELECT entity_id, country, token
            FROM (
              SELECT entity_id, country, unnest(string_split(name_norm, ' ')) AS token
              FROM targets
              UNION ALL
              SELECT entity_id, country, unnest(string_split(address_norm, ' ')) AS token
              FROM targets
            ) tokens
            WHERE length(token) >= 4
          ), allowed_tokens AS (
            SELECT country, token
            FROM target_tokens
            GROUP BY country, token
            HAVING count(*) <= {max_token_frequency}
          ), exact_matches AS (
            SELECT
              source1.entity_id AS source1_entity_id,
              target.entity_id AS candidate_entity_id
            FROM source1
            JOIN targets AS target
              ON source1.country = target.country
             AND (
               (source1.name_norm <> '' AND source1.name_norm = target.name_norm)
               OR
               (source1.address_norm <> '' AND source1.address_norm = target.address_norm)
             )
          ), token_matches AS (
            SELECT DISTINCT
              source1.entity_id AS source1_entity_id,
              target_tokens.entity_id AS candidate_entity_id
            FROM source1
            JOIN (
              SELECT entity_id, country, token
              FROM (
                SELECT entity_id, country, unnest(string_split(name_norm, ' ')) AS token
                FROM source1
                UNION ALL
                SELECT entity_id, country, unnest(string_split(address_norm, ' ')) AS token
                FROM source1
              ) source_tokens
              WHERE length(token) >= 4
            ) source_tokens
              ON source1.entity_id = source_tokens.entity_id
            JOIN target_tokens
              ON source_tokens.country = target_tokens.country
             AND source_tokens.token = target_tokens.token
            JOIN allowed_tokens
              ON target_tokens.country = allowed_tokens.country
             AND target_tokens.token = allowed_tokens.token
          ), matched AS (
            SELECT source1_entity_id, candidate_entity_id FROM exact_matches
            UNION
            SELECT source1_entity_id, candidate_entity_id FROM token_matches
          ), ranked AS (
            SELECT
              source1_entity_id,
              candidate_entity_id,
              row_number() OVER (
                PARTITION BY source1_entity_id ORDER BY candidate_entity_id
              ) AS candidate_rank
            FROM matched
          ), candidate_lists AS (
            SELECT
              source1_entity_id,
              string_agg(candidate_entity_id, ',' ORDER BY candidate_entity_id) AS candidate_entity_ids
            FROM ranked
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