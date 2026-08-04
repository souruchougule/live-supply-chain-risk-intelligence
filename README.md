# Live Global Supply-Chain & Economic Risk Intelligence Platform

An automated data pipeline that combines BigQuery public data, live weather data, and inconsistent shipment CSV files to identify supply-chain and economic risks.

## Project goal

Build a live, production-style data platform that ingests raw data, validates and cleans it, creates analytics-ready risk metrics, and powers a dashboard.

## Planned architecture

```text
BigQuery public data + External API + Raw CSV
                  │
                  ▼
          Python ingestion
                  │
                  ▼
     BigQuery Bronze / raw layer
                  │
                  ▼
 SQL and dbt transformations + quality tests
                  │
                  ▼
BigQuery Silver / cleaned layer → Gold / analytics layer
                  │
                  ├── Dashboard
                  ├── Alerts
                  └── Documentation
---
## Technologies

- BigQuery
- Python
- SQL
- dbt Core
- GitHub Actions
- Looker Studio
- Docker

## Status

In progress — repository setup.
