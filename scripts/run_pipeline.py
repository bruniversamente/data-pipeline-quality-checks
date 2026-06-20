"""Run the local data pipeline with DuckDB.

Usage:
    python scripts/run_pipeline.py
"""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data_pipeline.duckdb"
SQL_FILES = [
    ROOT / "sql" / "01_load_raw_tables.sql",
    ROOT / "sql" / "02_create_staging_tables.sql",
    ROOT / "sql" / "03_data_quality_checks.sql",
    ROOT / "sql" / "04_create_marts.sql",
    ROOT / "sql" / "05_kpi_queries.sql",
]


def run_sql_file(connection, sql_file: Path) -> None:
    print(f"\n--- Running {sql_file.name} ---")
    sql = sql_file.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]

    for statement in statements:
        result = connection.execute(statement)
        first_sql_line = next(
            (line.strip().lower() for line in statement.splitlines() if line.strip() and not line.strip().startswith("--")),
            "",
        )
        if first_sql_line.startswith("select") or first_sql_line.startswith("with"):
            print(result.fetchdf())


def main() -> None:
    con = duckdb.connect(str(DB_PATH))
    try:
        for sql_file in SQL_FILES:
            run_sql_file(con, sql_file)
    finally:
        con.close()
    print(f"\nPipeline finished. Database created at: {DB_PATH}")


if __name__ == "__main__":
    main()
