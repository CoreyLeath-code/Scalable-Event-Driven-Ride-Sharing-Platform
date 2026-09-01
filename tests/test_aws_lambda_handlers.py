import base64
import json

import pytest

from serverless.notification_worker import handler as notification_handler
from serverless.ride_event_processor import handler as ride_handler


class FakeSQS:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)
        return {"MessageId": "message-1"}


class FakeSNS:
    def __init__(self):
        self.messages = []

    def publish(self, **kwargs):
        self.messages.append(kwargs)
        return {"MessageId": "notification-1"}


def _encode(payload):
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")


def test_ride_event_processor_forwards_msk_record_with_idempotency_key(monkeypatch):
    monkeypatch.setenv("PROCESSED_EVENTS_QUEUE_URL", "https://sqs.example/processed")
    sqs = FakeSQS()
    event = {
        "records": {
            "ride.events-0": [
                {
                    "topic": "ride.events",
                    "partition": 0,
                    "offset": 42,
                    "value": _encode(
                        {
                            "event_type": "ride.requested",
                            "ride_id": "ride-123",
                            "rider_id": "rider-7",
                        }
                    ),
                }
            ]
        }
    }

    result = ride_handler.lambda_handler(event, None, sqs_client=sqs)

    assert result == {"processed": 1, "forwarded": 1}
    assert len(sqs.messages) == 1
    envelope = json.loads(sqs.messages[0]["MessageBody"])
    assert envelope["idempotency_key"] == "ride.events:0:42"
    assert envelope["source"] == "amazon-msk"
    assert envelope["event"]["ride_id"] == "ride-123"


def test_ride_event_processor_rejects_malformed_payload(monkeypatch):
    monkeypatch.setenv("PROCESSED_EVENTS_QUEUE_URL", "https://sqs.example/processed")
    event = {
        "records": {
            "ride.events-0": [
                {
                    "topic": "ride.events",
                    "partition": 0,
                    "offset": 43,
                    "value": _encode({"ride_id": "ride-123"}),
                }
            ]
        }
    }

    with pytest.raises(ValueError, match="event_type"):
        ride_handler.lambda_handler(event, None, sqs_client=FakeSQS())


def test_notification_worker_publishes_selected_lifecycle_events(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_TOPIC_ARN", "arn:aws:sns:us-east-1:123:ride-notifications")
    sns = FakeSNS()
    body = json.dumps(
        {
            "idempotency_key": "ride.events:0:50",
            "event": {
                "event_type": "trip.completed",
                "ride_id": "ride-123",
            },
        }
    )
    event = {"Records": [{"messageId": "message-1", "body": body}]}

    result = notification_handler.lambda_handler(event, None, sns_client=sns)

    assert result == {"batchItemFailures": [], "published": 1, "skipped": 0}
    assert len(sns.messages) == 1
    assert sns.messages[0]["Subject"] == "Ride event: trip.completed"


def test_notification_worker_skips_non_notification_events(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_TOPIC_ARN", "arn:aws:sns:us-east-1:123:ride-notifications")
    sns = FakeSNS()
    body = json.dumps({"event": {"event_type": "ride.requested", "ride_id": "ride-123"}})

    result = notification_handler.lambda_handler(
        {"Records": [{"messageId": "message-2", "body": body}]},
        None,
        sns_client=sns,
    )

    assert result == {"batchItemFailures": [], "published": 0, "skipped": 1}
    assert sns.messages == []


def test_notification_worker_returns_partial_batch_failure(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_TOPIC_ARN", "arn:aws:sns:us-east-1:123:ride-notifications")

    result = notification_handler.lambda_handler(
        {"Records": [{"messageId": "bad-message", "body": "not-json"}]},
        None,
        sns_client=FakeSNS(),
    )

    assert result["batchItemFailures"] == [{"itemIdentifier": "bad-message"}]
    assert result["published"] == 0
