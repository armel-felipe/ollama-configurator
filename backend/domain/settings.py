from typing import Any

DEFAULT_SENTINEL = "default"


def normalize_options(options: dict[str, Any]) -> dict[str, Any]:
    """Return only explicit overrides; preserve explicit falsy values."""
    return {
        name: value
        for name, value in options.items()
        if value is not None and value != DEFAULT_SENTINEL
    }
