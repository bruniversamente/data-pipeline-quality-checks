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


def main():
    con = duckdb.connect(str(DB_PATH))
    for sql_file in SQL_FILES:
        print(f"\n--- Running {sql_file.name} ---")
        sql = sql_file.read_text(encoding="utf-8")
        result = con.execute(sql)
        try:
            print(result.fetchdf())
        except Exception:
            print("Script executed.")
    con.close()
    print(f"\nPipeline finished. Database created at: {DB_PATH}")


if __name__ == "__main__":
    main()
