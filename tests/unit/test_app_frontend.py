from pathlib import Path

from backend.app import _resolve_frontend_dir


def test_backend_finds_source_frontend_when_no_override_is_configured(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_CONFIGURATOR_FRONTEND_DIR", raising=False)

    frontend_dir = _resolve_frontend_dir()
    expected = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    if expected.exists():
        assert frontend_dir == expected
    else:
        assert frontend_dir is None
