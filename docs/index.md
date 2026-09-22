# FinLens Documentation

FinLens is documented as a banking data platform with a small product surface and a deliberate
engineering backbone.

## Business Surface

- `Stress Pulse`
- `Failure Forensics`
- `Macro Transmission`
- `Predictive Analytics` (live, model-backed)
- `Wiki`

## Technical Surface

- `Live Pipeline`
- `Source Contracts`
- `Engineering Stack`
- `Data Quality`
- `Architecture Decisions`
- `Administration`
- `Wiki`

The Streamlit Architecture Decisions tab is the in-app knowledge surface. These markdown docs are
the repository-facing companion for code review, onboarding, and implementation history.

## Platform Stack

- Local filesystem (`data/raw`, Hive-partitioned by source and ingestion date) for bronze artifacts
- Airflow for orchestration
- dbt on DuckDB for transformations
- Snowflake as an optional, credential-gated dbt target
- FastAPI for health and telemetry
- Streamlit for presentation
- Cloudflare for the public edge
- Postgres for home control-plane sync

AWS S3 and Terraform were removed by ADR 0009; no cloud object store or infrastructure-as-code
remains on the live path.

## Active Source Policy

Approved:

- FDIC BankFind
- FDIC QBP
- FRED / ALFRED
- NIC current parent metadata only

Removed from active scope:

- SEC / EDGAR
- FR Y-9C
- SLOOS
- UBPR
- Filing Surveillance

## Architecture Contract

- Bronze: raw source preservation
- Silver: canonical normalized contracts
- Gold: dashboard-ready business metrics

Dashboards bind only to Gold.

## Documentation Map

- [Architecture](architecture.md) - platform shape, runtime surfaces, and deployment boundary
- [Data Flow](data-flow.md) - source intake, Bronze/Silver/Gold contracts, and serving rules
- [Validation](validation.md) - connector readiness, quality checks, test commands, and failure policy
- [Operations](operations.md) - local startup, health checks, secrets handling, and public presentation
- [Data Model](data-model.md) - current analytical model boundaries
- [Deployment Stack](deployment-stack.md) - production route and infrastructure notes
