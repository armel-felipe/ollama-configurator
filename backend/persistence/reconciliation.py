from typing import Any


def reconcile_saved_models(
    saved: dict[str, dict[str, Any]], installed: list[str]
) -> list[dict[str, Any]]:
    installed_set = set(installed)
    states = [
        {
            "model": model,
            "installed": True,
            "model_missing": False,
            "options": dict(saved.get(model, {})),
        }
        for model in installed
    ]
    states.extend(
        {
            "model": model,
            "installed": False,
            "model_missing": True,
            "options": dict(options),
        }
        for model, options in saved.items()
        if model not in installed_set
    )
    return states
