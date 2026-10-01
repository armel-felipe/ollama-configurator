from __future__ import annotations

import json
import queue
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class LogEvent:
    service: str
    level: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "service": self.service,
            "level": self.level,
            "message": self.message,
            "metadata": self.metadata,
        }


class LogStore:
    def __init__(self, max_events: int = 500) -> None:
        self._events: deque[LogEvent] = deque(maxlen=max_events)
        self._subscribers: list[queue.Queue[LogEvent]] = []
        self._lock = Lock()

    def emit(
        self,
        service: str,
        level: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> LogEvent:
        event = LogEvent(service, level, message, dict(metadata or {}))
        with self._lock:
            self._events.append(event)
            for subscriber in self._subscribers:
                subscriber.put(event)
        return event

    def snapshot(self, service: str | None = None) -> list[LogEvent]:
        with self._lock:
            events = list(self._events)
        return [event for event in events if service is None or event.service == service]

    def subscribe(self, service: str | None = None) -> Iterator[LogEvent]:
        subscriber: queue.Queue[LogEvent] = queue.Queue()
        with self._lock:
            self._subscribers.append(subscriber)
        try:
            while True:
                event = subscriber.get()
                if service is None or event.service == service:
                    yield event
        finally:
            with self._lock:
                if subscriber in self._subscribers:
                    self._subscribers.remove(subscriber)


LOG_STORE = LogStore()


def encode_sse(event: LogEvent) -> str:
    return f"data: {json.dumps(event.to_dict(), ensure_ascii=False)}\n\n"
