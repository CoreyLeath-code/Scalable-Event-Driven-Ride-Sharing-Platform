"""Security checks for sensitive driver-location endpoints."""

import httpx
import pytest

import api_router
from main import app


@pytest.mark.asyncio
async def test_driver_location_requests_require_a_configured_key(monkeypatch):
    monkeypatch.delenv("DRIVER_LOCATION_API_KEY", raising=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/driver-location/drivers")
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_driver_location_requests_reject_missing_or_wrong_key(monkeypatch):
    monkeypatch.setenv("DRIVER_LOCATION_API_KEY", "a-secret-only-used-in-ci")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        missing = await client.get("/driver-location/drivers")
        wrong = await client.get(
            "/driver-location/drivers/driver-1", headers={"X-Driver-API-Key": "wrong"}
        )
        count = await client.get("/driver-location/count")
    assert (missing.status_code, wrong.status_code, count.status_code) == (401, 401, 401)


@pytest.mark.asyncio
async def test_driver_location_requests_accept_correct_key(monkeypatch):
    monkeypatch.setenv("DRIVER_LOCATION_API_KEY", "a-secret-only-used-in-ci")

    class LocalStore:
        def count(self):
            return 2

    monkeypatch.setattr(api_router, "DRIVER_STORE", LocalStore())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/driver-location/count",
            headers={"X-Driver-API-Key": "a-secret-only-used-in-ci"},
        )
        liveness = await client.get("/driver-location/health")

    assert response.status_code == 200
    assert response.json() == {"active_drivers": 2}
    assert liveness.status_code == 200
