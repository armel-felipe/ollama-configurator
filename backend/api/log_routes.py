from collections.abc import Iterator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from backend.logs import LOG_STORE, encode_sse

router = APIRouter(prefix="/api/logs")


@router.get("")
def logs(service: str | None = Query(default=None)) -> list[dict[str, object]]:
    return [event.to_dict() for event in LOG_STORE.snapshot(service)]


@router.get("/stream")
def log_stream(service: str | None = Query(default=None)) -> StreamingResponse:
    def events() -> Iterator[str]:
        for event in LOG_STORE.snapshot(service):
            yield encode_sse(event)
        for event in LOG_STORE.subscribe(service):
            yield encode_sse(event)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
