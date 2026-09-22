# ADR 0008: Terraform Boundary

## Status

Superseded by ADR 0009 (VPS Local Storage).

## Decision

Use Terraform for S3, IAM, and Snowflake-adjacent resources while keeping DNS and app-hosting
setup as click-ops.

## Outcome

The only Terraform resources were the S3 buckets removed by ADR 0009, so the `terraform/`
directory and its CI workflow were deleted. Deployment is Caddy plus `docker-compose.prod.yml`;
there are no cloud resources left to provision.
