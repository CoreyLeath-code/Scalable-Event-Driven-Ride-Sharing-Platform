# Changelog

## [Unreleased]

### Added
- AWS Lambda ride-event processor for Amazon MSK batches with Kafka-derived idempotency keys.
- SQS buffering/DLQ handling and an SNS notification worker with partial-batch failure responses.
- Terraform reference infrastructure for Lambda, SQS, SNS, IAM, optional Amazon MSK, and CloudWatch observability.
- CloudWatch dashboard, alarms, operational SNS notifications, and a log-derived record-failure metric.
- Optional private IAM-authenticated MSK Serverless development environment and SNS-to-SQS integration probe.
- Real-MSK end-to-end latency evidence harness and manual VPC-runner workflow with explicit cost-estimate metadata.
- OIDC/Cognito-style JWT authentication boundary for sensitive driver-location endpoints.
- AWS Secrets Manager runtime resolver plus optional KMS/secret metadata/least-privilege reader-policy Terraform resources.
- Direct-PII guards in both Lambda stages and PII-safe application/event logging behavior.
- Kustomize dev/staging/prod overlays with parameterized images and environment configuration.
- Kubernetes promotion and rollback workflows with rendered/applied evidence artifacts and revision tracking.
- Credential-free unit tests for authentication, secrets, PII boundaries, broker connection contracts, AWS evidence helpers, and Kubernetes manifest policy.
- AWS, security/PII, real-MSK evidence, and Kubernetes promotion documentation.

### Changed
- README now distinguishes implemented controls, real measurements, unexecuted integration evidence, architecture targets, and remaining production gaps.
- Root Kafka/Redis/RabbitMQ adapters are directly importable and expose explicit pre-connect failure behavior.
- Event bus and driver telemetry consumer no longer log raw event bodies, coordinates, or validation payload details.
- Kubernetes deployment no longer uses `yourdockerhub/api-gateway:latest`; it includes rolling-update safety, probes, resource requests/limits, and revision history.
- Python packaging includes authentication, secret-resolution, and PII-policy modules.

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
