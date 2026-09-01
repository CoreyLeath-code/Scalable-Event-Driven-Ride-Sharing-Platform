import json

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

import auth
from pii_policy import assert_no_direct_pii, direct_pii_paths
from runtime_secrets import load_secret_json, resolve_driver_redis_url


class FakeSecretsClient:
    def __init__(self, payload):
        self.payload = payload
        self.secret_ids = []

    def get_secret_value(self, SecretId):
        self.secret_ids.append(SecretId)
        return {"SecretString": json.dumps(self.payload)}


@pytest.mark.asyncio
async def test_auth_is_credential_free_when_disabled(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    assert await auth.require_authenticated_request(None) is None


@pytest.mark.asyncio
async def test_auth_rejects_missing_bearer_when_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    with pytest.raises(HTTPException) as exc_info:
        await auth.require_authenticated_request(None)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_auth_delegates_token_verification_without_network(monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setattr(auth, "verify_bearer_token", lambda token: {"sub": token})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
    assert await auth.require_authenticated_request(credentials) == {"sub": "test-token"}


def test_secrets_manager_runtime_resolution_without_aws_credentials(monkeypatch):
    monkeypatch.setenv("DRIVER_LOCATION_REDIS_SECRET_ID", "ride-sharing/dev/runtime")
    client = FakeSecretsClient({"redis_url": "redis://private.example:6379/0"})
    assert resolve_driver_redis_url(client=client) == "redis://private.example:6379/0"
    assert client.secret_ids == ["ride-sharing/dev/runtime"]


def test_secret_loader_rejects_non_json_secret():
    class BadClient:
        def get_secret_value(self, SecretId):
            return {"SecretString": "not-json"}

    with pytest.raises(RuntimeError, match="valid JSON"):
        load_secret_json("secret-id", client=BadClient())


def test_pii_policy_detects_nested_direct_identifiers():
    payload = {"ride_id": "ride-1", "contact": {"email": "rider@example.com"}}
    assert direct_pii_paths(payload) == ["contact.email"]
    with pytest.raises(ValueError, match="Direct PII fields"):
        assert_no_direct_pii(payload)


def test_pii_policy_allows_pseudonymous_operational_identifiers():
    assert_no_direct_pii({"ride_id": "ride-1", "driver_id": "driver-7", "probe_id": "p-1"})
