# Sejmoskop - public part

[Sejmoskop](https://www.sejmoskop.pl) collects, processes and shows data about
the Polish parliament: the Sejm, the Senate and the European Parliament.

This repository is the **public part** of the project:

- `processing/` - the data processing pipeline, in Python.

The scrapers, the web app and the infrastructure code (Terraform) are
private, so they are not here.

## Scale

Measured in September 2026:

| What | Value |
|---|---|
| Votings | 73,000 |
| Individual votes | 34 million |
| Parliamentarians | 2,800 |
| Speeches | 222,000 |
| Years of data | 29 (since 1997) |
| Data in S3 | ~45 GB |
| Documents in OpenSearch | 1.3 million |
| Full refresh | every 3 days, ~90 minutes |
| AWS cost | ~25 USD / month |

## How the data flows

```
EventBridge Scheduler
  -> Step Functions (one state machine per data type and chamber)
       -> scrapers on AWS Batch        (private repo)  -> S3, raw data
       -> processing on AWS Batch      (this repo)     -> S3, processed data
       -> Lambda: Athena partitions, OpenSearch ingest, sitemap, cache refresh
  -> Athena / Glue tables for analytics
  -> OpenSearch for full-text search of speeches
  -> web app on Vercel                 (private repo)
```

The whole infrastructure is managed with Terraform.

## `processing/` - Python

The pipeline turns raw scraped data into clean tables and search documents.

- `pipelines/` - one pipeline per chamber (`sejm`, `senat`, `european`).
- `steps/`, `transformers/` - preprocessing, enrichment, analytics.
- `runners/aws/batch/` - entry points for AWS Batch jobs.
- `runners/aws/lambda/` - Lambda handlers (Athena partitions, OpenSearch
  ingest, sitemap data, cache refresh).
- `tests/` - pytest tests with small data samples.

Run the tests:

```bash
cd processing
poetry install
poetry run pytest
```

The Docker image (`processing/Dockerfile`) is the same one AWS Batch runs.

## License

MIT - see `LICENSE`.
