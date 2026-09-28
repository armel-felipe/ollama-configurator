import json
import os
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {"models": {}, "server": {}}


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"models": {}, "server": {}}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("invalid configuration JSON") from error
        if not isinstance(value, dict) or "models" not in value or "server" not in value:
            raise ValueError("invalid configuration shape")
        return value

    def save(self, config: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(config, indent=2, sort_keys=True) + "\n"
        descriptor, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=f".{self.path.name}.")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        except Exception:
            Path(temporary).unlink(missing_ok=True)
            raise
