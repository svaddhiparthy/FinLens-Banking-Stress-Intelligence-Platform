# ADR 0001: Cloud Object Storage

## Status

Superseded by ADR 0009 (VPS Local Storage).

## Context

FinLens needs a low-cost landing zone for raw API payloads and downstream artifact publication.

## Decision

Use AWS S3 for raw ingestion, DLQ, marts, docs, and Terraform state.

## Outcome

The S3 mirror was optional scaffold and never the live path; raw payloads already landed on the
local filesystem. ADR 0009 removed S3, boto3 and the S3 platform probe entirely. The bronze
landing zone is now `data/raw/source=<src>/ingestion_date=<date>/` on the host filesystem.
