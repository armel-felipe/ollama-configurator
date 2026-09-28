import httpx
import pytest

from backend.app import app
from backend.hardware.detector import HardwareDetector


@pytest.mark.asyncio
async def test_diagnostics_route_returns_local_machine_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    detector = HardwareDetector("Darwin", "arm64", 36 * 1024**3, "Apple")
    monkeypatch.setattr("backend.api.diagnostics_routes.get_hardware_detector", lambda: detector)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/hardware")

    assert response.status_code == 200
    assert response.json()["os"] == "macos"
    assert response.json()["backends"] == ["metal"]
