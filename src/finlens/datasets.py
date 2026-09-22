from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetBundle:
    failures: object
    metrics: object
    acquirers: object


def load_demo_bundle() -> DatasetBundle:
    import pandas as pd

    failures = pd.DataFrame(
        [
            {
                "bank_id": "bank-1",
                "bank_name": "Bank of Granite",
                "state": "NC",
                "year": 2009,
                "assets_millions": 2200,
                "acquirer": "First Citizens",
            },
            {
                "bank_id": "bank-2",
                "bank_name": "Silicon Valley Bank",
                "state": "CA",
                "year": 2023,
                "assets_millions": 209000,
                "acquirer": "First Citizens",
            },
            {
                "bank_id": "bank-3",
                "bank_name": "Signature Bank",
                "state": "NY",
                "year": 2023,
                "assets_millions": 118000,
                "acquirer": "Flagstar Bank",
            },
            {
                "bank_id": "bank-4",
                "bank_name": "Washington Mutual Bank",
                "state": "WA",
                "year": 2008,
                "assets_millions": 307000,
                "acquirer": "JPMorgan Chase",
            },
            {
                "bank_id": "bank-5",
                "bank_name": "Colonial Bank",
                "state": "AL",
                "year": 2009,
                "assets_millions": 25000,
                "acquirer": "BB&T",
            },
            {
                "bank_id": "bank-6",
                "bank_name": "First Republic Bank",
                "state": "CA",
                "year": 2023,
                "assets_millions": 229000,
                "acquirer": "JPMorgan Chase",
            },
            {
                "bank_id": "bank-7",
                "bank_name": "Guaranty Bank",
                "state": "TX",
                "year": 2009,
                "assets_millions": 13000,
                "acquirer": "BBVA Compass",
            },
            {
                "bank_id": "bank-8",
                "bank_name": "IndyMac Bank",
                "state": "CA",
                "year": 2008,
                "assets_millions": 32000,
                "acquirer": "OneWest Bank",
            },
        ]
    )
    metrics = pd.DataFrame(
        [
            {
                "series_id": "UNRATE",
                "date": "2008-01-01",
                "value": 5.0,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2008-06-01",
                "value": 5.6,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2008-09-01",
                "value": 6.2,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2009-03-01",
                "value": 8.7,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2009-09-01",
                "value": 9.8,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2010-06-01",
                "value": 9.4,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2022-06-01",
                "value": 3.6,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2023-01-01",
                "value": 3.4,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2023-03-01",
                "value": 3.5,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2023-06-01",
                "value": 3.6,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2023-09-01",
                "value": 3.8,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "UNRATE",
                "date": "2023-12-01",
                "value": 3.7,
                "metric_name": "Unemployment Rate",
            },
            {
                "series_id": "DGS10",
                "date": "2008-01-01",
                "value": 3.74,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2008-06-01",
                "value": 4.10,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2008-09-01",
                "value": 3.68,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2009-03-01",
                "value": 2.82,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2009-09-01",
                "value": 3.30,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2010-06-01",
                "value": 3.21,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2022-06-01",
                "value": 3.29,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2023-01-01",
                "value": 3.53,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2023-03-01",
                "value": 3.66,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2023-06-01",
                "value": 3.81,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2023-09-01",
                "value": 4.38,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS10",
                "date": "2023-12-01",
                "value": 4.02,
                "metric_name": "10Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2008-01-01",
                "value": 2.88,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2008-06-01",
                "value": 2.63,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2008-09-01",
                "value": 2.24,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2009-03-01",
                "value": 0.94,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2009-09-01",
                "value": 0.95,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2010-06-01",
                "value": 0.73,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2022-06-01",
                "value": 3.13,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2023-01-01",
                "value": 4.42,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2023-03-01",
                "value": 4.62,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2023-06-01",
                "value": 4.71,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2023-09-01",
                "value": 5.03,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "DGS2",
                "date": "2023-12-01",
                "value": 4.33,
                "metric_name": "2Y Treasury",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2008-01-01",
                "value": 211.08,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2008-09-01",
                "value": 218.78,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2009-09-01",
                "value": 215.97,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2022-06-01",
                "value": 296.31,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2023-01-01",
                "value": 299.17,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2023-03-01",
                "value": 301.84,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2023-06-01",
                "value": 303.84,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2023-09-01",
                "value": 307.48,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "CPIAUCSL",
                "date": "2023-12-01",
                "value": 308.74,
                "metric_name": "Consumer Price Index",
            },
            {
                "series_id": "NFCI",
                "date": "2022-06-01",
                "value": 0.14,
                "metric_name": "National Financial Conditions Index",
            },
            {
                "series_id": "NFCI",
                "date": "2023-03-01",
                "value": 0.42,
                "metric_name": "National Financial Conditions Index",
            },
            {
                "series_id": "NFCI",
                "date": "2023-12-01",
                "value": -0.08,
                "metric_name": "National Financial Conditions Index",
            },
            {
                "series_id": "BAA10Y",
                "date": "2022-06-01",
                "value": 2.35,
                "metric_name": "Moody's BAA minus 10Y Treasury",
            },
            {
                "series_id": "BAA10Y",
                "date": "2023-03-01",
                "value": 2.74,
                "metric_name": "Moody's BAA minus 10Y Treasury",
            },
            {
                "series_id": "BAA10Y",
                "date": "2023-12-01",
                "value": 1.68,
                "metric_name": "Moody's BAA minus 10Y Treasury",
            },
        ]
    )
    acquirers = pd.DataFrame(
        [
            {
                "acquirer": "First Citizens",
                "decade": "2020s",
                "assets_absorbed_millions": 211200,
            },
            {
                "acquirer": "Flagstar Bank",
                "decade": "2020s",
                "assets_absorbed_millions": 118000,
            },
            {
                "acquirer": "JPMorgan Chase",
                "decade": "2000s",
                "assets_absorbed_millions": 536000,
            },
            {
                "acquirer": "BB&T",
                "decade": "2000s",
                "assets_absorbed_millions": 25000,
            },
            {
                "acquirer": "BBVA Compass",
                "decade": "2000s",
                "assets_absorbed_millions": 13000,
            },
        ]
    )
    return DatasetBundle(failures=failures, metrics=metrics, acquirers=acquirers)


