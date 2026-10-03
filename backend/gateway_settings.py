from dataclasses import dataclass
from ipaddress import ip_address, ip_network
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
TAILSCALE_NETWORKS = (ip_network("100.64.0.0/10"), ip_network("fd7a:115c:a1e0::/48"))


@dataclass(frozen=True)
class GatewaySettingsState:
    host: str
    effective_host: str
    tailscale_ip: str | None = None
    port: int = GATEWAY_PORT
    pending_restart: bool = False
    options: tuple[str, ...] = GATEWAY_BIND_OPTIONS
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "effective_host": self.effective_host,
            "tailscale_ip": self.tailscale_ip,
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


def validate_tailscale_ip(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Informe um IP Tailscale válido")
    try:
        candidate = ip_address(normalized)
    except ValueError as error:
        raise ValueError("Informe um IP Tailscale válido, sem protocolo ou porta") from error
    if not any(candidate in network for network in TAILSCALE_NETWORKS):
        raise ValueError("Informe um IP Tailscale válido da rede Tailscale")
    return str(candidate)


class GatewaySettingsService:
    def __init__(self, store: ConfigStore) -> None:
        self.store = store

    def get(self, effective_host: str) -> GatewaySettingsState:
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        gateway = config.get("gateway", {})
        saved = gateway.get("host") if isinstance(gateway, dict) else None
        host = validate_gateway_host(saved) if saved is not None else DEFAULT_GATEWAY_HOST
        saved_tailscale_ip = gateway.get("tailscale_ip") if isinstance(gateway, dict) else None
        tailscale_ip = (
            validate_tailscale_ip(saved_tailscale_ip)
            if isinstance(saved_tailscale_ip, str)
            else None
        )
        return self._state(host, effective, tailscale_ip)

    def update(self, host: str, effective_host: str) -> GatewaySettingsState:
        desired = validate_gateway_host(host)
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        saved_gateway = config.get("gateway", {})
        gateway = dict(saved_gateway) if isinstance(saved_gateway, dict) else {}
        gateway["host"] = desired
        config["gateway"] = gateway
        self.store.save(config)
        LOG_STORE.emit(
            "configurator",
            "info",
            "Bind da gateway salvo",
            {"host": desired, "effective_host": effective},
        )
        saved_tailscale_ip = gateway.get("tailscale_ip")
        tailscale_ip = (
            validate_tailscale_ip(saved_tailscale_ip)
            if isinstance(saved_tailscale_ip, str)
            else None
        )
        return self._state(desired, effective, tailscale_ip)

    def update_tailscale_ip(
        self, value: str, effective_host: str
    ) -> GatewaySettingsState:
        tailscale_ip = validate_tailscale_ip(value)
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        saved_gateway = config.get("gateway", {})
        gateway = dict(saved_gateway) if isinstance(saved_gateway, dict) else {}
        host = validate_gateway_host(gateway.get("host", DEFAULT_GATEWAY_HOST))
        gateway["host"] = host
        gateway["tailscale_ip"] = tailscale_ip
        config["gateway"] = gateway
        self.store.save(config)
        LOG_STORE.emit(
            "configurator", "info", "IP Tailscale salvo", {"tailscale_ip": tailscale_ip}
        )
        return self._state(host, effective, tailscale_ip)

    def reset(self, effective_host: str) -> GatewaySettingsState:
        effective = validate_gateway_host(effective_host)
        config = self.store.load()
        config.pop("gateway", None)
        self.store.save(config)
        LOG_STORE.emit("configurator", "info", "Bind da gateway restaurado para padrão")
        return self._state(DEFAULT_GATEWAY_HOST, effective, None)

    @staticmethod
    def _state(
        host: str, effective_host: str, tailscale_ip: str | None
    ) -> GatewaySettingsState:
        return GatewaySettingsState(
            host=host,
            effective_host=effective_host,
            tailscale_ip=tailscale_ip,
            pending_restart=host != effective_host,
            warning=NETWORK_BIND_WARNING if host == NETWORK_GATEWAY_HOST else None,
        )
