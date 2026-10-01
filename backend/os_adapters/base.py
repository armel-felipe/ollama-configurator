from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class RestartResult:
    success: bool
    detail: str
    reapplied_models: list[str] = field(default_factory=list)


class SystemAdapter(Protocol):
    def get_environment(self, name: str) -> str | None: ...

    def set_environment(self, name: str, value: str) -> None: ...

    def remove_environment(self, name: str) -> None: ...

    def restart_ollama(self) -> RestartResult: ...

    def open_logs(self) -> None: ...
