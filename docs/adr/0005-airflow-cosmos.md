# ADR 0005: Airflow + Cosmos

## Status

Accepted, amended.

## Decision

Use Apache Airflow for orchestration and `astronomer-cosmos` for dbt task integration.

## Amendment

Airflow stands. The Cosmos integration was not adopted: `astronomer-cosmos` is not installed
(see `airflow/requirements.txt`), and the DAGs invoke dbt through the same
`scripts/run_local_pipeline.py --run-dbt-build` entry point a developer runs locally, via
`BashOperator`. This keeps a single code path between local and scheduled execution at the cost
of per-model task granularity in the Airflow UI.
