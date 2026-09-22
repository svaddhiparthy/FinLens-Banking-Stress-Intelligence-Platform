# DuckDB

DuckDB is the warehouse of record. `src/finlens/warehouse.py` loads the bronze payloads into the
`raw` schema of `.duckdb/finlens.duckdb`, and dbt builds the staging, intermediate and mart
layers on top.

- `ddl/001_create_marts.sql` — standalone mart DDL for a bare database.
- `export_marts.py` / `sql/export_marts.sql` — export gold tables to Parquet under `data/marts/`.
