from backend.config import settings
from backend.gateway import create_gateway_app
from backend.gateway_manager import GatewayProcessManager


def test_default_runtime_bind_is_localhost_only() -> None:
    assert settings.host == "127.0.0.1"
    assert GatewayProcessManager().host == "127.0.0.1"


def test_gateway_has_no_arbitrary_shell_route() -> None:
    paths = {route.path for route in create_gateway_app().routes}

    assert not any(
        any(token in path.lower() for token in ("shell", "exec", "command")) for path in paths
    )
    assert "/api/generate" in paths
    assert "/v1/chat/completions" in paths
