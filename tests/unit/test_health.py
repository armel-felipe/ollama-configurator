import httpx
import pytest

from backend.app import app


@pytest.mark.asyncio
async def test_health_endpoint_reports_running_application() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.1.12"
