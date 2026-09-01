import base64
import json

import pytest

from serverless.notification_worker import handler as notification_handler
from serverless.ride_event_processor import handler as ride_handler


class RecordingSqs:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)
        return {"MessageId": "m-1"}


class RecordingSns:
    def __init__(self):
        self.messages = []

    def publish(self, **kwargs):
        self.messages.append(kwargs)
        return {"MessageId": "n-1"}


def msk_event(payload):
    value = base64.b64encode(json.dumps(payload).encode()).decode()
    return {
        "records": {
            "ride.events-0": [
                {"topic": "ride.events", "partition": 0, "offset": 1, "value": value}
            ]
        }
    }


def test_msk_processor_rejects_direct_pii(monkeypatch):
    monkeypatch.setenv("PROCESSED_EVENTS_QUEUE_URL", "https://sqs.example/queue")
    sqs = RecordingSqs()
    with pytest.raises(ValueError, match="Direct PII"):
        ride_handler.lambda_handler(
            msk_event({"event_type": "ride.requested", "email": "rider@example.com"}),
            None,
            sqs_client=sqs,
        )
    assert sqs.messages == []


def test_notification_worker_returns_partial_failure_for_direct_pii(monkeypatch):
    monkeypatch.setenv("NOTIFICATION_TOPIC_ARN", "arn:aws:sns:us-east-1:123:topic")
    sns = RecordingSns()
    body = json.dumps(
        {"event": {"event_type": "trip.completed", "phone_number": "+15555550100"}}
    )
    result = notification_handler.lambda_handler(
        {"Records": [{"messageId": "bad-pii", "body": body}]},
        None,
        sns_client=sns,
    )
    assert result["batchItemFailures"] == [{"itemIdentifier": "bad-pii"}]
    assert sns.messages == []
