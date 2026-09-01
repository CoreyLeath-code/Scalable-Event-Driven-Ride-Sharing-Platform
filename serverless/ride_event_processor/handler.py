"""Process Amazon MSK ride events and forward normalized envelopes to SQS."""

import base64
import json
import logging
import os
from typing import Any

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def _decode_record(record: dict[str, Any]) -> dict[str, Any]:
    """Decode one Lambda Amazon MSK record into a JSON object."""
    encoded_value = record.get("value")
    if not isinstance(encoded_value, str) or not encoded_value:
        raise ValueError("MSK record is missing a base64-encoded value")

    try:
        decoded = base64.b64decode(encoded_value).decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("MSK record value is not valid base64-encoded JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("MSK event payload must be a JSON object")

    event_type = payload.get("event_type") or payload.get("type")
    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("MSK event payload requires event_type or type")

    return payload


def _build_envelope(record: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Preserve Kafka metadata for traceability and downstream idempotency."""
    topic = str(record.get("topic", "unknown"))
    partition = record.get("partition", "unknown")
    offset = record.get("offset", "unknown")

    return {
        "idempotency_key": f"{topic}:{partition}:{offset}",
        "source": "amazon-msk",
        "topic": topic,
        "partition": partition,
        "offset": offset,
        "event": payload,
    }


def _default_sqs_client():
    import boto3  # type: ignore[import-not-found]

    return boto3.client("sqs")


def lambda_handler(event: dict[str, Any], _context: Any, *, sqs_client: Any = None) -> dict[str, int]:
    """Forward an MSK Lambda batch to the configured SQS queue.

    The function intentionally fails the invocation on malformed input or an SQS send
    failure. Amazon MSK/Lambda can then retry the batch. Consumers must therefore use the
    emitted idempotency_key because delivery is at-least-once.
    """
    queue_url = os.environ.get("PROCESSED_EVENTS_QUEUE_URL")
    if not queue_url:
        raise RuntimeError("PROCESSED_EVENTS_QUEUE_URL is required")

    client = sqs_client or _default_sqs_client()
    processed = 0

    for partition_records in event.get("records", {}).values():
        if not isinstance(partition_records, list):
            raise ValueError("MSK event records must be grouped into lists")

        for record in partition_records:
            payload = _decode_record(record)
            envelope = _build_envelope(record, payload)
            client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(envelope, separators=(",", ":"), sort_keys=True),
            )
            processed += 1

    LOGGER.info("Forwarded %s MSK ride events to SQS", processed)
    return {"processed": processed, "forwarded": processed}
