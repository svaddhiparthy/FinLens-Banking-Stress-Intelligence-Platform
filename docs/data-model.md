# Data Model

The current FinLens data model is intentionally small and durable.

## Bronze

Raw source snapshots are stored unchanged, tagged with ingest metadata.

Approved Bronze domains:
- `fdic_bankfind`
- `fdic_qbp`
- `fdic_qbp_annual_legacy` (preserved pre-cutover annual aggregate)
- `fred`
- `nic_current_parent`

## Silver

Silver normalizes provider payloads into canonical internal contracts.

Core Silver entities:
- `institution_current`
- `quarter`
- `failure_event`
- `macro_observation`
- `industry_aggregate`
- `pipeline_run`

## Gold

Gold is the only layer the UI reads from. The tables below are the current contracts, built by
dbt into the `marts` schema (plus `dim_acquirer`, materialized during the DuckDB load).

| Table | Grain |
| --- | --- |
| `bank_quarterly_risk_facts` | one row per `(cert, quarter)` - CAMELS-aligned risk ratios |
| `fct_bank_failures` | one row per failed institution |
| `fct_financial_metrics` | one row per `(series_id, date)`, incremental |
| `fct_stress_pulse` | one row per quarter of industry aggregates |
| `fct_stress_pulse_annual_legacy` | one row per preserved pre-cutover annual aggregate |
| `dim_date` | one row per date |
| `dim_state` | one row per state code (Type 1) |
| `dim_acquirer` | one row per `(acquirer, decade)` |
| `snapshots.dim_bank_snapshot` | SCD Type 2 history of the bank dimension |

## Rules

- no dashboard reads raw provider fields directly
- no threshold logic lives in UI code
- every displayed metric must have a source and as-of date
- annual legacy QBP rows never replace or masquerade as true quarterly rows

## Warehouse Target

DuckDB is the warehouse of record (ADR 0002, ADR 0009), with dbt owning the transformation
contract between the raw, staging, intermediate and mart schemas. Snowflake remains an optional,
credential-gated dbt target. Streamlit reads stable Gold outputs regardless of which engine
backs them.
