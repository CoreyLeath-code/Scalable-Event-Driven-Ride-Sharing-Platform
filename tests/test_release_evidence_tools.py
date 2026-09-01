import json
from pathlib import Path

import pytest

from scripts.aws_msk_e2e import (
    estimate_variable_cost_usd,
    percentile,
    unwrap_sns_sqs_body,
)
from scripts.k8s_release_evidence import build_evidence, manifest_sha256


def test_percentile_interpolates_deterministically():
    values = [10.0, 20.0, 30.0, 40.0]
    assert percentile(values, 0.50) == 25.0
    assert percentile(values, 0.95) == pytest.approx(38.5)


def test_cost_estimate_uses_explicit_pricing_inputs():
    cost = estimate_variable_cost_usd(
        samples=100,
        elapsed_seconds=3600,
        lambda_requests_per_million_usd=1.0,
        sqs_requests_per_million_usd=1.0,
        sns_publishes_per_million_usd=1.0,
        msk_cluster_hourly_usd=2.0,
    )
    assert cost == pytest.approx(2.0007)


def test_unwrap_sns_sqs_body_returns_original_notification_payload():
    body = json.dumps(
        {"Message": json.dumps({"event_type": "trip.completed", "probe_id": "p1"})}
    )
    assert unwrap_sns_sqs_body(body)["probe_id"] == "p1"


def test_release_evidence_records_manifest_hash(tmp_path: Path):
    manifest = tmp_path / "rendered.yaml"
    manifest.write_text("kind: Deployment\n", encoding="utf-8")
    evidence = build_evidence(
        action="promote",
        environment="staging",
        image="ghcr.io/example/app:v1.2.3",
        git_sha="abc123",
        manifest=manifest,
        deployment_status="rendered",
    )
    assert evidence["manifest_sha256"] == manifest_sha256(manifest)
    assert evidence["deployment_status"] == "rendered"


def test_production_evidence_requires_immutable_digest(tmp_path: Path):
    manifest = tmp_path / "rendered.yaml"
    manifest.write_text("kind: Deployment\n", encoding="utf-8")
    with pytest.raises(ValueError, match="immutable image digest"):
        build_evidence(
            action="promote",
            environment="prod",
            image="ghcr.io/example/app:latest",
            git_sha="abc123",
            manifest=manifest,
            deployment_status="rendered",
        )
