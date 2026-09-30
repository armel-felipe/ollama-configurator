import pytest

from backend.app import app
from backend.gateway_manager import GatewayStatus


class FakeManager:
    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0

    def start(self) -> GatewayStatus:
        self.started += 1
        return GatewayStatus("starting", pid=101)

    def stop(self) -> GatewayStatus:
        self.stopped += 1
        return GatewayStatus("stopped")


@pytest.mark.asyncio
async def test_application_lifecycle_starts_and_stops_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = FakeManager()
    monkeypatch.setattr("backend.app.get_gateway_manager", lambda: manager)

    async with app.router.lifespan_context(app):
        assert manager.started == 1
        assert manager.stopped == 0

    assert manager.stopped == 1
