from backend.logs import LogEvent, LogStore


def test_log_store_keeps_recent_events_and_filters_by_service() -> None:
    store = LogStore(max_events=2)
    store.emit("gateway", "info", "Gateway iniciado", {"port": 11435})
    store.emit("ollama", "info", "Perfil aplicado", {"think": False})
    store.emit("configurator", "error", "Falha ao carregar")

    events = store.snapshot(service="gateway")

    assert len(events) == 0
    assert store.snapshot()[0].service == "ollama"
    assert store.snapshot()[1].service == "configurator"


def test_log_event_serializes_safe_operational_metadata() -> None:
    event = LogEvent("ollama", "info", "Perfil aplicado", {"think": False})

    payload = event.to_dict()

    assert payload["service"] == "ollama"
    assert payload["metadata"] == {"think": False}
    assert isinstance(payload["timestamp"], str)
