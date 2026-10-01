from dataclasses import dataclass
from typing import Any

from backend.logs import LOG_STORE
from backend.persistence.store import ConfigStore

DEFAULT_GATEWAY_HOST = "127.0.0.1"
NETWORK_GATEWAY_HOST = "0.0.0.0"
GATEWAY_BIND_OPTIONS = (DEFAULT_GATEWAY_HOST, NETWORK_GATEWAY_HOST)
GATEWAY_PORT = 11435
NETWORK_BIND_WARNING = (
    "O gateway ficará acessível pelas interfaces de rede desta máquina. "
    "Use apenas em uma rede confiável e considere configurar uma chave de API."
)


@dataclass(frozen=True)
class GatewaySettingsState:
    host: str
    effective_host: str
    port: int = GATEWAY_PORT
    pending_restart: bool = False
    options: tuple[str, ...] = GATEWAY_BIND_OPTIONS
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "effective_host": self.effective_host,
            "port": self.port,
            "pending_restart": self.pending_restart,
            "options": list(self.options),
            "warning": self.warning,
        }


def validate_gateway_host(host: str) -> str:
    if host not in GATEWAY_BIND_OPTIONS:
        allowed = ", ".join(GATEWAY_BIND_OPTIONS)
        raise ValueError(f"host do gateway inválido; use um destes valores: {allowed}")
    return host


class GatewaySettingsService:
    def __init__(self, store: ConfigStore) -> None:
        self.store = store

    def get(self, effective_host: str) -> GatewaySettingsState:
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        gateway = config.get("gateway", {})
        saved = gateway.get("host") if isinstance(gateway, dict) else None
        host = validate_gateway_host(saved) if saved is not None else DEFAULT_GATEWAY_HOST
        return self._state(host, effective)

    def update(self, host: str, effective_host: str) -> GatewaySettingsState:
        desired = validate_gateway_host(host)
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        config["gateway"] = {"host": desired}
        self.store.save(config)
        LOG_STORE.emit(
            "configurator",
            "info",
            "Bind da gateway salvo",
            {"host": desired, "effective_host": effective},
        )
        return self._state(desired, effective)

    def reset(self, effective_host: str) -> GatewaySettingsState:
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        config.pop("gateway", None)
        self.store.save(config)
        LOG_STORE.emit("configurator", "info", "Bind da gateway restaurado para padrão")
        return self._state(DEFAULT_GATEWAY_HOST, effective)

    @staticmethod
    def _state(host: str, effective_host: str) -> GatewaySettingsState:
        return GatewaySettingsState(
            host=host,
            effective_host=effective_host,
            pending_restart=host != effective_host,
            warning=NETWORK_BIND_WARNING if host == NETWORK_GATEWAY_HOST else None,
        )
