# v1.1.0

v1.1.0 packages the repository's currently implemented reference components and release evidence. It is not a claim of a complete production ride-sharing service.

## Added

- Redis-backed driver-location storage for scaled API replicas.
- NGINX least-connections routing with liveness/readiness checks.
- CI coverage for gateway routing, shared-state reads, and one-replica loss.
- Release assets: wheel, source distribution, SHA-256 checksums, and SPDX SBOM.
- A version-tagged GHCR container image.

## Verification

The release workflow runs formatting, linting, static typing, unit tests, the deterministic benchmark harness, Python package build, and Docker image build before publishing assets.

## Scope

The release distributes a reference implementation. It does not provide production identity, payment processing, PII controls, a fully integrated broker/deployment environment, or a production availability commitment.
