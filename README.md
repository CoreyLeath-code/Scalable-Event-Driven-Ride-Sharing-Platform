# Scalable Event-Driven Ride-Sharing Platform

[![CI](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/ci.yml)
[![System Hygiene Matrix](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/hygiene-matrix.yml/badge.svg)](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/hygiene-matrix.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-Event%20Streaming-231F20?logo=apachekafka&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes&logoColor=white)

This repository models a high-throughput ride-sharing backend using event-driven services,
asynchronous dispatch flows, geospatial matching primitives, dynamic pricing, containerized
deployment assets, and GitHub Actions validation.

The project is intentionally scoped as a production-style reference implementation: measured
local benchmarks are recorded separately from target architecture goals so the README stays
useful for engineering review, not just system-design storytelling.


This repository models an event-driven ride-request flow with local matching, pricing, location-store, benchmark, and deployment-reference components. It does not run a complete live ride-sharing service with production brokers, payments, identity, or real driver/rider data. Production deployment would require integrated broker and datastore environments, authentication and PII controls, real image/service configuration, end-to-end reliability testing, and operational ownership.

## Architecture flowchart

```mermaid
flowchart LR
    Client --> Gateway --> Services[API + workers] --> Events[(Event bus)] --> Store[(State)]
```

### Quickstart and local validation

The supported local path should be reproducible from a clean checkout. The inferred stack for this repository is **Python/platform services**.

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
pytest -q
```

If the project uses external services, model artifacts, cloud credentials, or private data, start them through documented local fixtures or mocks. Never place secrets or identifiable records in the repository.

### Research-style metrics and benchmarks

| Evidence | Required record |
|---|---|
| Correctness | Test command, commit SHA, runtime, and pass/fail result |
| Performance | Warm-up, sample count, concurrency, median, p95, p99, throughput, and memory |
| Data/model quality | Dataset version, split strategy, leakage controls, calibration, subgroup results, and uncertainty |
| Runtime | Image digest, health-check latency, resource limits, and rollback target |
| Security | Dependency, secret, SAST, container, and SBOM results |

A benchmark number belongs in a versioned artifact tied to a commit and hardware/runtime description. Engineering benchmarks must not be presented as clinical, financial, safety, or model-quality validation without the appropriate domain evidence.

### Extended Q&A

**What is production-ready for this repository?**  
A reproducible build, tested public contract, controlled configuration, observable runtime, documented security boundary, versioned artifacts, and a tested rollback path.

**What must remain explicit?**  
The intended use, excluded use, data/credential handling, model or algorithm limitations, and which metrics are measured versus aspirational.

**What should be completed next?**  
Use the linked production-readiness issue for this repository as the checklist. Resolve missing tests, deployment instructions, observability, supply-chain controls, and release evidence before attaching a production claim.


## Architecture

```text
Client / Rider App
    |
    v
API Gateway
    |
    v
Ride Requested Event
    |
    v
Event Bus (Kafka / Redis / RabbitMQ style)
    |
    +--> Matching Engine
    |        |
    |        v
    |   Driver Assigned Event
    |
    +--> Pricing Engine
    |
    +--> Notification / Payment / Trip Lifecycle Extensions
```

Core components:

- API gateway for external ride requests.
- Driver location store for active driver telemetry.
- Event bus abstraction for asynchronous pub/sub workflows.
- Matching engine for candidate ranking and driver assignment.
- Pricing engine for demand/supply surge calculations.
- Infrastructure examples for Docker, Kubernetes, and GitHub Actions.

## Research Benchmarks and Recorded Metrics

Benchmark evidence is generated from the reviewed checkout rather than copied into the README. Run `make reproduce` to regenerate the published benchmark and coverage artifacts.

The command writes `benchmark-results.json`, `coverage.xml`, and `reproducibility-results.json` in the repository root. The JSON artifact records the exact commands, tracked-file inventory, quality-check outcomes, line coverage, and the benchmark payload from that run.

### Measured Microbenchmarks

| Area | Workload | Generated evidence |
| --- | --- | --- |
| Event bus publish and delivery | In-memory `ride.requested` events | `benchmark.event_bus` in `benchmark-results.json` |
| Matching engine | Synthetic candidates and a deterministic pickup | `benchmark.matching` in `benchmark-results.json` |
| Driver location store | In-memory telemetry upserts | `benchmark.location_store` in `benchmark-results.json` |
| Pricing engine | Synthetic demand and supply inputs | `benchmark.pricing` in `benchmark-results.json` |

### Engineering Quality Metrics

| Metric | Reproduced by | Artifact |
| --- | --- | --- |
| Tracked repository files | `git ls-files` inventory | `engineering.tracked_repository_files` in `reproducibility-results.json` |
| Python files | `git ls-files` inventory | `engineering.python_files` in `reproducibility-results.json` |
| Test files | `git ls-files` inventory | `engineering.test_files` in `reproducibility-results.json` |
| Test and line coverage | `pytest --cov=.` | `coverage.xml` and `coverage.line_coverage_percent` |
| GitHub Actions workflows | `.github/workflows/` inventory | `engineering.github_actions_workflows` |
| Infrastructure manifests | Docker and Kubernetes inventory | `engineering.infrastructure_manifests` |
| Formatting, linting, and typing | Black, Ruff, and mypy | `commands.format`, `commands.lint`, and `commands.type_check` |
| Benchmark JSON validation | `python -m json.tool benchmark-results.json` | `commands.benchmark_json` |

### Architecture Target Metrics

These are design targets for a production deployment, not claims from the local benchmark harness.

| Capability | Target |
| --- | ---: |
| Ride request throughput | 10,000+ requests/sec |
| Driver telemetry ingestion | 5,000+ events/sec |
| Matching latency | P95 under 15 ms |
| Event bus propagation | Under 10 ms |
| Service availability | 99.9% |
| Autoscaling response | Under 8 seconds |
| CI/CD pipeline time | Under 90 seconds |

## Validation and CI

The repository now has an explicit validation path:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
make reproduce
```

GitHub Actions now:

- Uses `actions/setup-python` pip caching with `requirements.txt` and `requirements-dev.txt`.
- Installs runtime and development dependencies from committed requirement files.
- Fails on formatting, linting, type, test, and benchmark errors instead of bypassing failures.
- Validates benchmark JSON before artifact upload.
- Uploads benchmark artifacts for review.
- Writes workflow summaries to `GITHUB_STEP_SUMMARY`.
- Builds the actual root `Dockerfile` in the CD workflow instead of nonexistent service Dockerfiles.

## Quick Start

```bash
git clone https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform.git
cd Scalable-Event-Driven-Ride-Sharing-Platform
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest
```

For the containerized demo:

```bash
docker compose up --build
curl http://localhost:8000/driver-location/health
```

The Compose profile starts the repository's root driver-location API and validates its
health endpoint. Kafka and the additional service boundaries remain architectural extension
points; they are not started by this local demo profile.

## Load-balanced driver-location API

The public Compose endpoint at port `8000` is NGINX; it forwards to internal `driver-location-api` replicas using least-connections routing. `/driver-location/health` is a liveness probe, while `/driver-location/ready` verifies the configured Redis-backed driver store. The CI integration job validates the NGINX configuration, replica routing, shared-state read, and continued readiness after one replica stops; `EXPOSE_INSTANCE_ID=true` is limited to that test and is disabled by default.

## Event Flow

```text
ride.requested -> matching-service
driver.matched -> trip-service
trip.started -> pricing-service
trip.completed -> payment-service
payment.processed -> notification-service
```

## Project Structure

```text
.
|-- .github/workflows/       # CI, hygiene matrix, and CD workflows
|-- benchmarks/              # JSON-producing benchmark harness
|-- docs/                    # Architecture and metrics notes
|-- infra/kubernetes/        # Deployment and HPA manifests
|-- load-tests/              # Locust scenario
|-- services/                # Service entrypoint examples
|-- shared/                  # Shared config, logging, schema, and event bus adapters
|-- tests/                   # Core behavior tests
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
|-- requirements.txt
|-- requirements-dev.txt
`-- README.md
```

## Industry-Readiness Notes

Upgrades included in this pass:

- Repaired invalid Python imports that prevented test collection.
- Replaced placeholder tests with behavior tests for event bus, matching, location store, and pricing.
- Added a deterministic benchmark harness with JSON output.
- Added `pyproject.toml` for formatting, pytest, coverage, and Ruff configuration.
- Added committed runtime dependencies in `requirements.txt`.
- Removed CI soft-fail patterns and stale cache keys.
- Updated CD actions to current major versions and valid Docker build inputs.
- Replaced corrupted README sections and stale repository links.

Known remaining gaps for a full production release:

- Coverage is 54%; next priority is adding API router, consumer, broker adapter, and service integration tests.
- `docker-compose.yml` still references service directories that are architectural placeholders.
- Kafka, Redis Streams, and RabbitMQ adapters pass Docker-backed publish/consume round trips in the dedicated CI job. The suite is isolated from the Docker-free unit-test path.
- Kubernetes manifests should be parameterized with real image names and deployment environments.
- Authentication, authorization, secrets management, and PII controls need implementation before production use.
# [![CI](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/ci.yml/badge.svg?branch=docs%2Fportfolio-readme-production-scalable-event-driven-ride-sharing-platform)](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/ci.yml) [![Hygiene](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/hygiene-matrix.yml/badge.svg?branch=docs%2Fportfolio-readme-production-scalable-event-driven-ride-sharing-platform)](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/actions/workflows/hygiene-matrix.yml)
