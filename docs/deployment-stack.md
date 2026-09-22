# Deployment Stack

Target public application:

- `https://srivaddhiparthy.com/finlens/`

## Runtime Layers

| Layer | Tool | Responsibility |
|---|---|---|
| Edge | Cloudflare | DNS, optional proxying, Turnstile, branded domain |
| Presentation | Streamlit | Business and technical surfaces |
| API | FastAPI | Health, telemetry, and machine-facing status |
| Orchestration | Airflow | Scheduled ingestion, transforms, and sync |
| Raw storage | Local filesystem | Bronze landing zone, Hive-partitioned by source and ingestion date |
| Modeling | dbt | Silver, Intermediate, and Gold transformation contracts |
| Warehouse | DuckDB | Warehouse of record; Snowflake stays an optional credential-gated dbt target |
| Provisioning | Caddy + `docker-compose.prod.yml` | No infrastructure-as-code: there are no cloud resources to provision (ADR 0009) |
| Control sync | Postgres | Home copy of telemetry and control-plane snapshots |

## Ready-To-Plug Posture

- FDIC ingestion runs locally now.
- FRED, QBP, and NIC are wired behind connector values and source contracts.
- Raw payloads land on the local filesystem under `data/raw`, with a rotation policy retaining
  the newest version per source.
- Airflow DAGs call the current bootstrap, transform, and sync scripts.
- dbt models reflect the approved source set.
- FastAPI exposes `/health`, `/healthz`, `/telemetry/events`, and `/telemetry/summary`.
- Postgres sync creates the target schema and tables when `POSTGRES_SYNC_DSN` is supplied.

## Current Production State

- Public app: `https://srivaddhiparthy.com/finlens/`
- Health endpoint: `https://finlens-api.vaddhiparthy.vip/healthz`
- Monitoring: `https://uptime.vaddhiparthy.vip`
- FDIC, FRED, QBP, and NIC source runs are populated when the corresponding source contracts are enabled.
- Runtime data is mounted into the production containers instead of being hard-coded into images.
- Caddy is the only public ingress path for application traffic.

## Monitoring

Uptime Kuma should watch:

- `https://finlens-api.vaddhiparthy.vip/healthz`
- `vpn.vaddhiparthy.vip`
- `192.168.100.100` over WireGuard
