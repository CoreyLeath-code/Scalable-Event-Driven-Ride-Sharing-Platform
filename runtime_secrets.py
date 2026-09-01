"""Runtime secret resolution with AWS Secrets Manager and local-development fallback."""

import json
import os
from typing import Any


def _default_secrets_client():
    import boto3

    return boto3.client("secretsmanager")


def load_secret_json(secret_id: str, *, client: Any = None) -> dict[str, Any]:
    """Fetch a JSON secret without logging or returning AWS response metadata."""
    secrets_client = client or _default_secrets_client()
    response = secrets_client.get_secret_value(SecretId=secret_id)
    secret_string = response.get("SecretString")
    if not isinstance(secret_string, str) or not secret_string:
        raise RuntimeError("Secrets Manager secret must contain a non-empty SecretString")

    try:
        payload = json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Secrets Manager secret must contain valid JSON") from exc

    if not isinstance(payload, dict):
        raise TypeError("Secrets Manager secret JSON must be an object")
    return payload


def resolve_driver_redis_url(*, client: Any = None) -> str | None:
    """Resolve Redis URL from Secrets Manager when configured, otherwise local env."""
    secret_id = os.getenv("DRIVER_LOCATION_REDIS_SECRET_ID")
    if not secret_id:
        return os.getenv("DRIVER_LOCATION_REDIS_URL")

    secret = load_secret_json(secret_id, client=client)
    redis_url = secret.get("redis_url")
    if not isinstance(redis_url, str) or not redis_url.strip():
        raise RuntimeError("Runtime secret requires a non-empty redis_url field")
    return redis_url
