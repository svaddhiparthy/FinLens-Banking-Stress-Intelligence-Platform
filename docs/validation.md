# Validation

FinLens uses validation at three levels: connector readiness, data quality, and application smoke checks.

## Connector Readiness

```powershell
python .\scripts\run_local_pipeline.py --check-connectors
```

This checks whether optional source and platform connectors have enough configuration to run.

## Data Quality

Two independent gates:

- **dbt tests**, run as part of `dbt build`: six generic `not_null` tests across the marts plus
  the singular `assert_bank_quarterly_risk_facts_unique_grain` test, which asserts composite
  uniqueness of the `(cert, quarter)` gold grain.
- **Expectation suites** under `great_expectations/`, in Great Expectations v3 suite format.
  They are executed by `great_expectations/validate.py`, not by the Great Expectations library:
  the repository's own `great_expectations/` directory shadows the PyPI package, so the runner
  is a self-contained evaluator of the same suite JSON. It reads the mart from DuckDB, writes a
  GX-shaped result, and exits non-zero on any failure.

```powershell
python great_expectations/validate.py
```

Primary validation intent:

- confirm required fields and the declared grain;
- bound null rates and value ranges rather than asserting perfection where the data does not
  support it (for example `tier1_rwa_ratio` after the 2020Q1 CBLR election);
- assert freshness, so a stale warehouse fails instead of serving silently;
- separate load-time checks from serving-layer checks;
- keep quality failures visible before dashboard use.

## Code and App Checks

```powershell
python -m ruff check .
python -m pytest -q
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

The smoke script validates imports, chart construction, and demo stress-lab execution.

## No Fake Passes

Validation should fail loudly when required local data or connector settings are absent. Placeholder success is worse than an honest readiness gap.
