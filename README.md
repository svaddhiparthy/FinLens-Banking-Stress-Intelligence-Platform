# FinLens — Banking Stress Intelligence Platform

[![CI](https://github.com/Vaddhiparthy/FinLens-Banking-Stress-Intelligence-Platform/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/Vaddhiparthy/FinLens-Banking-Stress-Intelligence-Platform/actions/workflows/main.yml)

FinLens is a self-hosted data platform that turns free U.S. bank regulatory data into a
governed analytical warehouse. Python clients ingest four public sources into an immutable,
Hive-partitioned bronze landing zone; a DuckDB warehouse loads those payloads into a `raw`
schema; dbt builds staging, intermediate and mart layers on top, including a Kimball-style star
schema, an SCD Type 2 snapshot, and a per-bank-quarter gold mart at the `(cert, quarter)` grain;
quality gates (dbt tests plus an expectation-suite runner) sit at the load and serve boundaries;
and Airflow schedules the whole thing through the same Python entry points that run locally.
FastAPI and Streamlit read only from the gold layer. A discrete-time hazard model is one
downstream consumer of the gold mart, not the centre of the system.

Project page: [vaddhiparthy.com/FinLens-Banking-Stress-Intelligence-Platform](https://vaddhiparthy.com/FinLens-Banking-Stress-Intelligence-Platform/)

---

## Architecture

```text
 PUBLIC SOURCES          INGESTION                BRONZE (immutable)
 ┌──────────────┐    ┌──────────────────┐    ┌─────────────────────────────────────┐
 │ FDIC failed  │    │ ingestion/fdic   │    │ data/raw/                           │
 │ banks (CSV)  │───▶│ ingestion/qbp    │───▶│   source=<src>/                     │
 │ FDIC QBP     │    │ ingestion/fred   │    │     ingestion_date=YYYY-MM-DD/      │
 │ FRED series  │    │ ingestion/nic    │    │       <uuid>.json  (+ .data.json,   │
 │ Institutions │    │                  │    │        .source.xlsx for QBP)        │
 └──────────────┘    │ retry/backoff    │    │ data/dlq/  (same layout)            │
                     │ watermarks       │    │ rotation: keep N newest per source  │
                     │ run recorder     │    └──────────────────┬──────────────────┘
                     └──────────────────┘                       │
                                            finlens.warehouse.initialise_local_duckdb
                                                                │
 ┌──────────────────────────────────────────────────────────────▼───────────────────┐
 │ DuckDB  .duckdb/finlens.duckdb                                                   │
 │                                                                                  │
 │  raw.*          ──▶  SILVER  dbt staging views   stg_fdic_failed_banks,          │
 │  (loaded from            (models/staging)        stg_fdic_qbp, stg_fred_…,       │
 │   bronze payloads)                               stg_nic_current_parent          │
 │                                     │                                            │
 │                                     ▼                                            │
 │                 INTERMEDIATE  int_failures_with_macro_context (view)             │
 │                                     │                                            │
 │                                     ▼                                            │
 │  ml.training_dataset ─▶  GOLD  fct_bank_failures · fct_financial_metrics         │
 │  (feature panel)               fct_stress_pulse · bank_quarterly_risk_facts      │
 │                                dim_date · dim_state · dim_acquirer               │
 │                                snapshots.dim_bank_snapshot (SCD Type 2)          │
 └──────────────────────────────────┬───────────────────────────────────────────────┘
                                    │
              QUALITY GATES ────────┤  dbt tests (generic + singular, run in dbt build)
                                    │  expectation-suite runner on the gold mart
                                    │  platform readiness probes (airflow/dbt/raw/postgres)
                                    │
                                    ▼
 SERVING            FastAPI (/health · /failures · /metrics · /telemetry)
                    Streamlit surfaces (business · data engineering · AI · wiki)
                    Postgres control-plane sync (telemetry + run snapshots)
                    Discrete-time hazard model (downstream consumer of the gold mart)

 ORCHESTRATION      Airflow 3.3.1, LocalExecutor — 7 DAGs calling the same entry points
```

Nothing in the serving layer reads below the gold layer, and no orchestrator-only code path
exists: every DAG task is a `BashOperator` calling a plain entry point under `scripts/` or `ml/`
that a developer can run identically on a laptop.

---

## Data sources

Four sources are orchestrated through `finlens.bootstrap.SOURCE_DEFINITIONS`. Endpoints are
configured in `src/finlens/config.py` and overridable through `.env`.

| Key | Source | What lands | Cadence | Required config |
|---|---|---|---|---|
| `fdic` | FDIC failed bank list (CSV download) | One JSON payload per run: every historical failure with cert, city, state, acquirer, closing date | daily DAG | none (public URL default) |
| `qbp` | FDIC Quarterly Banking Profile | The release page is crawled for the newest time-series workbook; the exact `.xlsx` is preserved with its SHA-256 alongside a normalized per-quarter JSON (balance sheet, income, loan performance, ratios) | quarterly DAG | `FDIC_QBP_SOURCE_URL` |
| `fred` | FRED (St. Louis Fed) macro series — `UNRATE`, `DGS10`, `DGS2`, `BAA10Y`, `NFCI`, `CPIAUCSL` | Series metadata plus full observation history, one payload per series | daily DAG | `FRED_API_KEY` |
| `nic` | Current-institution reference contract | Normalized to the NIC current-parent column shape (`rssd_id`, `fdic_certificate_number`, `current_parent_*`, charter class, regulator, assets) | quarterly DAG | `NIC_CURRENT_PARENT_SOURCE_URL` |

Two further FDIC/FFIEC feeds are used outside the four-source loop:

- `ingestion/fdic_institutions.py` pulls the per-CERT quarterly Call Report panel and entity
  metadata from the FDIC BankFind `/financials` and `/institutions` endpoints (paged at 10,000
  rows, ~34 curated CAMELS-relevant fields). Run as a module it writes a bronze partition; the
  dataset builder calls its fetch layer directly to materialize `ml.training_dataset`.
- `ml/scripts/b1_download.py` retrieves FFIEC CDR bulk Call Report zips for an offline
  point-in-time study (`ml/finlens_ml/ffiec_pit.py`) that re-derives features from
  originally-filed values instead of FDIC-restated ones. It is a research path, not part of the
  scheduled pipeline.

The NIC connector ships with a default URL that resolves to the FDIC institutions endpoint, so
`rssd_id` and `current_parent_*` land null until a true NIC artifact URL is configured; the
column contract is what downstream models bind to.

---

## Pipeline and orchestration

Seven DAGs live in `airflow/dags/`, all built on `common.py` defaults (`retries=2`,
`retry_delay=5 min`, `depends_on_past=False`, `catchup=False`).

| DAG | Schedule | Task chain |
|---|---|---|
| `dag_ingest_fdic` | `0 2 * * *` | `run_local_pipeline.py --sources fdic --skip-warehouse` |
| `dag_ingest_fred` | `@daily` | `run_local_pipeline.py --sources fred --skip-warehouse` |
| `dag_ingest_qbp` | `0 3 1 3,6,9,12 *` | ingest QBP, then `TriggerDagRunOperator` fires `dag_transform_and_quality` and waits for completion (60 s poke, `reset_dag_run=True`) |
| `dag_ingest_nic` | `0 2 1 3,6,9,12 *` | refreshes the institution reference one hour ahead of the QBP-triggered chain |
| `dag_transform_and_quality` | `0 4 * * *` | `run_local_pipeline.py --skip-ingestion --run-dbt-build --probe-platform --sync-postgres` |
| `dag_sync_control_plane` | `CronTriggerTimetable("0 5 * * *", UTC)`, `max_active_runs=1`, 30 min timeout | collect Airflow evidence → sync control plane to Postgres → retention sweep (90-day snapshots, 365-day telemetry, 500-row batches) |
| `dag_ml_retrain` | `None` (triggered deliberately) | `build_dataset` → `train_and_register` → `metric_gate` → `export_web_data`; a failed gate blocks promotion and leaves the prior champion alias in place. The quarterly chain stops at the transform DAG — retraining is not fired automatically on every load |

Reliability mechanics, as implemented:

- **Retries.** HTTP calls go through `finlens.http.build_session`, which wraps
  `requests.Session.request` in a tenacity policy: exponential backoff (1 s → 30 s), five
  attempts, `raise_for_status()` inside the retry boundary, 30 s default timeout. Airflow adds
  two task-level retries on top.
- **Watermark-based incremental ingestion.** The FRED client reads the series `last_updated`
  timestamp from the metadata endpoint and compares it against `data/state/fred_watermarks.json`.
  Unchanged series are skipped without downloading observations, and the watermark is only
  advanced after the payload is written. On the warehouse side,
  `fct_financial_metrics` is an incremental dbt model keyed on `(series_id, date)`.
  The other three sources are full snapshots — each run lands a complete, replayable payload.
- **Dead-letter zone.** `IngestionTarget.create(source, dead_letter=True)` routes a write to
  `data/dlq/source=…/ingestion_date=…/` under the same partition scheme as bronze, and the
  rotation policy sweeps both zones. Today a source exception marks the flow `Failed` in the
  control plane and re-raises so the Airflow task fails visibly, rather than silently
  quarantining a payload.
- **Retention.** `finlens.retention.rotate_raw_and_dlq` keeps the newest `keep` `ingestion_date`
  partitions per source (default 1) and purges the rest, so the landing zone does not grow
  unbounded on a single VPS disk.
- **Run recording.** `PipelineRunRecorder` wraps every stage (connector readiness, ingestion,
  warehouse rebuild, rotation, dbt build, probes, Postgres sync), writing per-stage status,
  detail and metadata to `data/state/` for the control-plane surfaces.
- **Fail-closed readiness.** `run_local_pipeline.py --check-connectors` reports which sources
  have their required configuration; `--probe-platform` fails the run when the Airflow, dbt,
  raw-storage or Postgres probes are not `Ready`.

---

## Data model

| Layer | Location | Materialization | Contents |
|---|---|---|---|
| Bronze | `data/raw/source=<src>/ingestion_date=<date>/<uuid>.json` | files on disk | Verbatim payloads plus an ingest manifest (source URL, `ingested_at`, record count, SHA-256 for binary artifacts). Written atomically via temp file + `os.replace`. |
| Load | `raw.*` in DuckDB | tables | `initialise_local_duckdb` reads the newest manifest per source, cleans field names/encoding, and rebuilds `raw.fdic_failed_banks_raw`, `raw.fred_observations_raw`, `raw.fdic_qbp_raw`, `raw.fdic_qbp_annual_legacy_raw`, `raw.nic_current_parent_raw`. |
| Silver | `dbt/models/staging` | views | `stg_fdic_failed_banks`, `stg_fdic_qbp`, `stg_fred_observations`, `stg_nic_current_parent` — column selection and naming contract over `raw`. |
| Intermediate | `dbt/models/intermediate` | view | `int_failures_with_macro_context` — reusable join surface for the failure grain. |
| Gold | `dbt/models/marts`, `dbt/models/reference` | tables | Facts and dimensions the serving layer binds to. |

Key tables and their grain:

| Table | Grain | Notes |
|---|---|---|
| `bank_quarterly_risk_facts` | one row per `(cert, quarter)` | The primary gold mart. CAMELS-aligned ratios (`noncurrent_to_loans`, `nco_to_loans`, `tier1_rwa_ratio`, `tier1_leverage`, `equity_to_assets`, `roa`) sourced from `ml.training_dataset` in the same DuckDB file. `tier1_rwa_ratio` is deliberately nullable after 2020Q1 because of the Community Bank Leverage Ratio election, so it carries a null-rate threshold instead of a `not_null` test. |
| `fct_bank_failures` | one row per failed institution | cert, name, city, state, closing date, acquirer. |
| `fct_financial_metrics` | one row per `(series_id, date)` | Incremental model over FRED observations. |
| `fct_stress_pulse` | one row per quarter | Industry aggregates from the QBP workbook (net income, ROA, NIM, yields, funding cost, noncurrent and charge-off rates, AFS/HTM unrealized losses). |
| `dim_date` | one row per date | Generated 1990-01-01 forward. |
| `dim_state` | one row per state code | Type 1 reference dimension. |
| `dim_acquirer` | one row per `(acquirer, decade)` | Built during the DuckDB load. |

**SCD Type 2.** `dbt/snapshots/dim_bank_snapshot.sql` snapshots the bank dimension with
`strategy='check'` on `bank_name` and `state`, `unique_key='bank_id'`, into a dedicated
`snapshots` schema. dbt maintains `dbt_valid_from` / `dbt_valid_to`, so a renamed or
re-domiciled institution produces a new version row instead of an in-place update: Type 2 for
bank-like dimensions, Type 1 for state, Type 0 for date.

---

## Data quality

Three independent gates, all fail-closed:

**dbt tests** (`dbt build` runs models, snapshots and tests in one pass): six generic `not_null`
tests across `fct_bank_failures` (`bank_id`, `state`), `fct_financial_metrics` (`series_id`),
`fct_stress_pulse` (`quarter`) and `bank_quarterly_risk_facts` (`cert`, `quarter`), plus one
singular test, `assert_bank_quarterly_risk_facts_unique_grain.sql`, which asserts composite
uniqueness of `(cert, quarter)` without requiring a package dependency.

**Expectation suites.** `great_expectations/expectations/bank_quarterly_risk_facts.json` is a
valid Great Expectations v3 expectation-suite document holding 20 expectations: row-count bounds,
column existence, null-rate thresholds with `mostly` tolerances (including the intentionally
tolerant `tier1_rwa_ratio` at 0.55), value-range checks, and a freshness expectation that the
maximum quarter is at least 2024Q4. **The Great Expectations library does not execute it.** The
repository's own top-level `great_expectations/` package shadows the PyPI distribution, so
`great_expectations/validate.py` is a self-contained evaluator that reads the same suite JSON,
runs each supported expectation type against the materialized mart in DuckDB, writes a
GX-shaped validation result, and exits non-zero on any failure. The committed result
(`great_expectations/validation_result.json`) shows 20/20 passing over 448,661 rows.
`expectations/on_load.json` and `on_serve.json`, with their checkpoint YAML, describe the
load-time and serve-time suites in the same format.

**Platform probes.** `finlens.platform_probes` checks the Airflow DAG folder and health
endpoint, the dbt project, the raw landing zone and Postgres; `--probe-platform` raises if any
required probe is not `Ready`.

---

## Serving

- **FastAPI** (`api/`): `/health` and `/healthz` readiness payloads (connector report, pipeline
  status, Postgres probe), `/failures` and `/banks/{bank_id}` over `marts.fct_bank_failures`,
  `/metrics/{series_id}` over `marts.fct_financial_metrics`, and `/telemetry/events` +
  `/telemetry/summary`, all backed by Pydantic schemas. The read paths fall back to a small
  in-code fixture when the warehouse has not been built yet.
- **Streamlit** (`streamlit_app/`): business, data engineering, AI engineering and wiki surfaces,
  reading gold marts and committed artifacts only.
- **Control-plane sync** (`scripts/sync_control_plane_to_postgres.py`): creates
  `finlens.telemetry_events` and `finlens.control_plane_snapshots` if absent and syncs new
  telemetry and run snapshots, with a retention job bounded by age and batch size.
- **Parquet export** (`duckdb/`): mart DDL and `COPY … (FORMAT PARQUET)` export for the gold
  tables.

## Downstream model

One consumer of `bank_quarterly_risk_facts` and `ml.training_dataset` is a discrete-time hazard
model (`ml/`): a calibrated, monotone-constrained, 12-seed bagged LightGBM estimating the
probability that an institution fails within four quarters, built on 34 engineered CAMELS
features. Out-of-time evaluation over the final 28 quarters (118,943 bank-quarters, 66 real
failures, base rate 0.055%) gives PR-AUC 0.301, ROC-AUC 0.855 and recall@200 0.545, against a
logit benchmark at PR-AUC 0.153 — all from `ml/artifacts/metrics_h4.json`. The retrain DAG gates
promotion on `ml/scripts/metric_gate.py`. A retrieval module (`rag/`) answers questions over
cited failure-cause documents and live model scores; synthesis calls an OpenRouter-compatible
chat-completions endpoint when `OPENROUTER_API_KEY` is set and otherwise falls back to an
extractive, fully-cited answer.

---

## Run it locally

Requires Python 3.11–3.13 (`pyproject.toml` pins `>=3.11,<3.14`). Dependencies are locked with
`uv` (`uv.lock`); any equivalent virtualenv workflow works if you install from `pyproject.toml`
instead.

```bash
uv sync --all-groups
cp .env.example .env          # fill FRED_API_KEY and the optional source URLs
```

Ingest, rebuild the DuckDB warehouse, and rotate the landing zone:

```bash
uv run python scripts/run_local_pipeline.py --check-connectors   # readiness only
uv run python scripts/run_local_pipeline.py --allow-missing-connectors
```

Build the dbt layers (staging → intermediate → marts → snapshot → tests) against DuckDB:

```bash
FINLENS_DUCKDB_PATH=.duckdb/finlens.duckdb \
  uv run dbt build --project-dir dbt --profiles-dir dbt --target local
```

Run the gold-mart expectation suite:

```bash
uv run python great_expectations/validate.py    # exit 0 = all expectations pass
```

Serve the local surfaces (both bind to loopback and are local-only, not public endpoints):

```bash
uv run python -m uvicorn api.main:app --host 127.0.0.1 --port 8010   # local API
uv run streamlit run streamlit_app/app.py --server.address 127.0.0.1 --server.port 8501
```

Bring up Airflow locally (LocalExecutor, Postgres metadata DB; the UI is served on
`localhost:8080` on your machine only):

```bash
docker compose -f airflow/docker-compose.yml up
```

On Windows, `scripts/start_finlens.ps1` and `scripts/start_api.ps1` wrap the same commands.

---

## Testing

```bash
uv run ruff check .
uv run pytest -q
```

The suite is 117 tests (102 passing, 15 skipped when optional ML dependencies or a built DuckDB
file are absent), collected from `tests/` and `ml/tests/` per `pyproject.toml`. Coverage spans
ingestion clients and the storage-path contract, config and bootstrap, retention and
control-plane retention, telemetry, the warehouse builder, the FastAPI app, Airflow schedule
assertions, Streamlit view-model and chart smoke tests, and the ML feature/label/evaluation
layer — including `test_no_billable_imports`, which fails if anything under `ml/` imports a
billable client.

## Continuous integration

| Workflow | Trigger | Steps |
|---|---|---|
| `.github/workflows/pr.yml` | pull request | `uv sync --all-groups`, `ruff check .`, `pytest` |
| `.github/workflows/main.yml` | push to `main` | `uv sync --all-groups`, `pytest` (the badge above) |
| `.github/workflows/nightly.yml` | manual dispatch | connector readiness check with `--allow-missing-connectors`, then `pytest -q` |

All three run on `ubuntu-latest` with Python 3.11 and `astral-sh/setup-uv`.

---

## Repository layout

```text
airflow/            7 DAGs, Dockerfile, LocalExecutor compose stack
ingestion/          Per-source clients: fdic, fdic_institutions, fred, nic, qbp
src/finlens/        Shared platform code
  config.py           pydantic-settings configuration
  bootstrap.py        source registry + orchestrated source runs
  http.py             retrying session factory
  ingestion/base.py   partition-path contract, DLQ routing, retry policy
  state.py            watermark and run-state persistence
  storage.py          atomic JSON/bytes writers
  retention.py        raw + DLQ rotation policy
  warehouse.py        bronze -> DuckDB raw/marts loader
  platform_probes.py  Airflow/dbt/storage/Postgres readiness
  pipeline_runs.py    per-stage run recorder
dbt/                staging · intermediate · marts · reference · snapshots · tests
great_expectations/ expectation suites, checkpoints, suite runner, results
duckdb/             mart DDL and Parquet export
api/                FastAPI routers, schemas, services
streamlit_app/      analyst surfaces and shared presentation lib
ml/                 feature/label/train/evaluate pipeline, artifacts, tests
rag/                retrieval + cited-answer module
scripts/            pipeline, dbt, sync, retention and startup entry points
snowflake/          optional credential-gated warehouse DDL and load scripts
docs/ml/            model write-ups rendered by the AI Engineering surface
tests/              platform and surface tests
```

---

## Design decisions

- **Warehouse lifecycle.** Snowflake in the early phase, then DuckDB plus Parquet as the
  sustainable long-term engine. DuckDB is the warehouse of record; Snowflake remains an
  optional, credential-gated dbt target (`snowflake/`, `dbt/profiles.yml`).
- **Kimball star schema.** Explicit fact and dimension tables rather than one wide
  denormalized output.
- **SCD strategy.** Type 2 for bank-like dimensions, Type 1 for state, Type 0 for date.
- **Orchestration without an orchestrator-only code path.** Airflow schedules the pipeline,
  but the Cosmos dbt integration was not adopted: DAGs invoke the same Python entry points
  used locally through `BashOperator`.
- **Quality split.** dbt tests for structural assertions; expectation suites and runtime
  probes for source-to-serving validation.
- **VPS local storage instead of S3 and Terraform.** Bronze is the VPS local filesystem under
  a Hive-partitioned layout with a rotation policy, so there are no cloud resources to
  provision. Deployment is Caddy plus `docker-compose.prod.yml`.

---

## License

Proprietary. All rights reserved. No use, copying, modification, distribution, or commercial use
is permitted without the author's prior written authorization. See the `LICENSE` file.

**Author:** Surya Vaddhiparthy
