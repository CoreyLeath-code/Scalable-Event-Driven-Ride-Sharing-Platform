"""Measure a real MSK -> Lambda -> SQS -> Lambda -> SNS path from inside the MSK VPC."""

import argparse
import json
import math
import os
import statistics
import time
import uuid
from pathlib import Path
from typing import Any


class MskTokenProvider:
    def __init__(self, region: str):
        self.region = region

    def token(self) -> str:
        from aws_msk_iam_sasl_signer import MSKAuthTokenProvider

        token, _ = MSKAuthTokenProvider.generate_auth_token(self.region)
        return token


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile_value
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def unwrap_sns_sqs_body(body: str) -> dict[str, Any]:
    outer = json.loads(body)
    message = outer.get("Message")
    if not isinstance(message, str):
        raise ValueError("SQS probe message does not contain an SNS Message string")
    payload = json.loads(message)
    if not isinstance(payload, dict):
        raise TypeError("SNS Message must decode to a JSON object")
    return payload


def estimate_variable_cost_usd(
    *,
    samples: int,
    elapsed_seconds: float,
    lambda_requests_per_million_usd: float,
    sqs_requests_per_million_usd: float,
    sns_publishes_per_million_usd: float,
    msk_cluster_hourly_usd: float,
) -> float:
    lambda_requests = samples * 2
    sqs_requests = samples * 4
    sns_publishes = samples
    return (
        lambda_requests / 1_000_000 * lambda_requests_per_million_usd
        + sqs_requests / 1_000_000 * sqs_requests_per_million_usd
        + sns_publishes / 1_000_000 * sns_publishes_per_million_usd
        + elapsed_seconds / 3600 * msk_cluster_hourly_usd
    )


def env_float(name: str) -> float:
    value = os.getenv(name)
    return float(value) if value else 0.0


def build_producer(bootstrap_servers: list[str], region: str) -> Any:
    from kafka import KafkaProducer

    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SASL_SSL",
        sasl_mechanism="OAUTHBEARER",
        sasl_oauth_token_provider=MskTokenProvider(region),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        request_timeout_ms=30000,
        api_version_auto_timeout_ms=30000,
    )


def receive_probe(sqs_client: Any, queue_url: str, probe_id: str, timeout_seconds: int) -> int:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10,
        )
        for message in response.get("Messages", []):
            receipt_handle = message.get("ReceiptHandle")
            payload = unwrap_sns_sqs_body(message["Body"])
            if receipt_handle:
                sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
            if payload.get("probe_id") == probe_id:
                return time.time_ns()
    raise TimeoutError(f"Probe {probe_id} was not observed before timeout")


def main() -> None:
    import boto3

    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster-arn", required=True)
    parser.add_argument("--topic", default="ride.events")
    parser.add_argument("--probe-queue-url", required=True)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evidence/aws-msk-integration-results.json"),
    )
    args = parser.parse_args()

    if args.samples < 1:
        raise ValueError("samples must be at least 1")

    region = os.getenv("AWS_REGION", "us-east-1")
    kafka_client = boto3.client("kafka", region_name=region)
    sqs_client = boto3.client("sqs", region_name=region)
    brokers = kafka_client.get_bootstrap_brokers(ClusterArn=args.cluster_arn)
    bootstrap = brokers.get("BootstrapBrokerStringSaslIam")
    if not bootstrap:
        raise RuntimeError("MSK cluster did not return IAM bootstrap brokers")

    producer = build_producer(bootstrap.split(","), region)
    latencies_ms: list[float] = []
    run_started = time.time()

    try:
        for index in range(args.samples):
            probe_id = f"probe-{uuid.uuid4()}"
            sent_ns = time.time_ns()
            payload = {
                "event_type": "trip.completed",
                "ride_id": f"synthetic-{index}",
                "probe_id": probe_id,
                "sent_at_ns": sent_ns,
            }
            producer.send(args.topic, payload).get(timeout=30)
            received_ns = receive_probe(
                sqs_client,
                args.probe_queue_url,
                probe_id,
                args.timeout_seconds,
            )
            latencies_ms.append((received_ns - sent_ns) / 1_000_000)
    finally:
        producer.close(timeout=10)

    elapsed_seconds = time.time() - run_started
    pricing_inputs = {
        "lambda_requests_per_million_usd": env_float("LAMBDA_REQUESTS_PER_MILLION_USD"),
        "sqs_requests_per_million_usd": env_float("SQS_REQUESTS_PER_MILLION_USD"),
        "sns_publishes_per_million_usd": env_float("SNS_PUBLISHES_PER_MILLION_USD"),
        "msk_cluster_hourly_usd": env_float("MSK_CLUSTER_HOURLY_USD"),
    }
    cost = estimate_variable_cost_usd(
        samples=args.samples,
        elapsed_seconds=elapsed_seconds,
        **pricing_inputs,
    )

    result = {
        "schema_version": 1,
        "status": "measured",
        "measurement_scope": "amazon-msk-to-lambda-to-sqs-to-lambda-to-sns-probe-sqs",
        "sample_count": len(latencies_ms),
        "latency_ms": {
            "min": min(latencies_ms),
            "mean": statistics.mean(latencies_ms),
            "p50": percentile(latencies_ms, 0.50),
            "p95": percentile(latencies_ms, 0.95),
            "p99": percentile(latencies_ms, 0.99),
            "max": max(latencies_ms),
        },
        "cost": {
            "measurement_type": "request-count-and-runtime estimate",
            "estimated_variable_cost_usd": cost,
            "pricing_inputs": pricing_inputs,
            "pricing_inputs_complete": all(value > 0 for value in pricing_inputs.values()),
            "includes_data_transfer_or_cloudwatch": False,
            "note": "This is not AWS billing data. Use Cost Explorer after the run for billed-cost evidence.",
        },
        "cluster_arn": args.cluster_arn,
        "topic": args.topic,
        "aws_region": region,
        "elapsed_seconds": elapsed_seconds,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
