# Changelog

## [Unreleased]

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
