# Expectation suites

Great Expectations-format expectation suites and the runner that executes them.

| Path | Purpose |
|---|---|
| `expectations/bank_quarterly_risk_facts.json` | 20 expectations on the gold mart: row-count bounds, column existence, null-rate thresholds (`mostly`), value ranges, and a freshness floor on the maximum quarter |
| `expectations/on_load.json`, `expectations/on_serve.json` | Load-time and serve-time suites |
| `checkpoints/*.yml` | Checkpoint definitions naming each suite |
| `validate.py` | The runner. Loads the mart from DuckDB, evaluates the suite, writes a GX-shaped result to `uncommitted/`, and exits non-zero on any failure |
| `validation_result.json` | Last committed run: 20/20 expectations passing |

Important: the Great Expectations **library** does not execute these suites. This directory
shadows the `great_expectations` PyPI package on the import path, so `validate.py` is a
self-contained evaluator of the same suite JSON (schema, null-rate, range, freshness and
row-count expectation types). The suite documents are valid GX v3 format and would run unchanged
against a real GX context if the name collision were removed.

```bash
python great_expectations/validate.py    # exit 0 = all expectations pass
```
