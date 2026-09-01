"""Publish selected ride lifecycle events from SQS to an SNS notification topic."""

import json
import logging
import os
from typing import Any

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

NOTIFIABLE_EVENTS = {
    "driver.matched",
    "trip.started",
    "trip.completed",
    "payment.processed",
}


def _default_sns_client():
    import boto3  # type: ignore[import-not-found]

    return boto3.client("sns")


def _extract_event(body: str) -> dict[str, Any]:
    try:
        envelope = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("SQS record body must be valid JSON") from exc

    if not isinstance(envelope, dict):
        raise ValueError("SQS record body must contain a JSON object")

    payload = envelope.get("event", envelope)
    if not isinstance(payload, dict):
        raise ValueError("Notification payload must be a JSON object")

    return payload


def lambda_handler(
    event: dict[str, Any], _context: Any, *, sns_client: Any = None
) -> dict[str, Any]:
    """Process an SQS batch and report per-message failures for safe retries."""
    topic_arn = os.environ.get("NOTIFICATION_TOPIC_ARN")
    if not topic_arn:
        raise RuntimeError("NOTIFICATION_TOPIC_ARN is required")

    client = sns_client or _default_sns_client()
    failures: list[dict[str, str]] = []
    published = 0
    skipped = 0

    for record in event.get("Records", []):
        message_id = str(record.get("messageId", "unknown"))
        try:
            payload = _extract_event(str(record.get("body", "")))
            event_type = payload.get("event_type") or payload.get("type")

            if event_type not in NOTIFIABLE_EVENTS:
                skipped += 1
                continue

            client.publish(
                TopicArn=topic_arn,
                Subject=f"Ride event: {event_type}",
                Message=json.dumps(payload, separators=(",", ":"), sort_keys=True),
            )
            published += 1
        except Exception:
            LOGGER.exception("Failed to process SQS notification record %s", message_id)
            failures.append({"itemIdentifier": message_id})

    LOGGER.info(
        "Notification batch complete: published=%s skipped=%s failed=%s",
        published,
        skipped,
        len(failures),
    )
    return {
        "batchItemFailures": failures,
        "published": published,
        "skipped": skipped,
    }
