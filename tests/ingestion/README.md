# Ingestion Tests

Unit tests for the source clients and the shared ingestion contract.

- `test_base.py` — partition-path layout and dead-letter routing for `IngestionTarget`.
- `test_fdic.py`, `test_fred.py`, `test_qbp.py` — payload shaping, watermark behaviour, and
  workbook normalization, all against fixtures (no network calls).
