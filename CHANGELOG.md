# Changelog

## [Unreleased]

### Added
- AWS Lambda ride-event processor for Amazon MSK batches with Kafka-derived idempotency keys.
- SQS buffering and dead-letter queue handling between asynchronous AWS workers.
- AWS Lambda notification worker with SQS partial-batch failure responses and SNS publication.
- Terraform reference infrastructure for Lambda, SQS, SNS, CloudWatch Logs, IAM, and optional Amazon MSK event-source mapping.
- Credential-free Lambda unit tests and Terraform validation workflow.
- AWS serverless architecture and deployment documentation.

### Changed
- README now documents the hybrid container/service + serverless architecture and separates measured evidence from architecture targets.
- Python packaging now includes the `serverless` package tree.

## [1.1.0] - 2026-08-21
### Added
- Redis-backed driver-location state for scaled API replicas.
- NGINX least-connections gateway configuration and readiness checks.
- CI coverage for gateway routing, shared-state access, and single-replica loss.
- Reproducible release artifacts: Python wheel, source distribution, checksums, SPDX SBOM, and version-tagged GHCR image.

### Changed
- Release automation now validates a semantic tag, quality gates, package build, and container build before publishing.

## [1.0.0] - 2025-06-01
### Added
- Event producer/consumer modules using Kafka.
- REST API for ride requests.
- Basic data model and database schema for ride and driver tables.
- Unit tests for core modules.
