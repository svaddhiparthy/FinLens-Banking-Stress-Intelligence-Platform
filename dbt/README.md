# dbt

The transformation layer, materialized on DuckDB (`profiles.yml` target `local`) with an
optional credential-gated Snowflake target.

| Path | Materialization | Contents |
|---|---|---|
| `models/staging` | view | `stg_fdic_failed_banks`, `stg_fdic_qbp`, `stg_fred_observations`, `stg_nic_current_parent` over the DuckDB `raw` schema |
| `models/intermediate` | view | `int_failures_with_macro_context` |
| `models/marts` | table | `fct_bank_failures`, `fct_financial_metrics` (incremental on `series_id, date`), `fct_stress_pulse`, `bank_quarterly_risk_facts` (grain: `cert, quarter`) |
| `models/reference` | table | `dim_date`, `dim_state` |
| `snapshots` | snapshot | `dim_bank_snapshot` — SCD Type 2, `strategy='check'` on `bank_name`/`state` |
| `tests` | singular test | `assert_bank_quarterly_risk_facts_unique_grain.sql` |

Build everything (models, snapshot and tests) in one pass:

```bash
FINLENS_DUCKDB_PATH=.duckdb/finlens.duckdb dbt build --project-dir dbt --profiles-dir dbt --target local
```
