import json
import os
from collections.abc import Iterator
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.gateway_service import GatewayService
from backend.ollama.client import get_ollama_client
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore


def create_gateway_app(
    store: ConfigStore | None = None,
    client: Any | None = None,
    api_key: str | None = None,
) -> FastAPI:
    selected_store = store or ConfigStore(user_data_dir() / "config.json")
    selected_client = client or get_ollama_client()
    service = GatewayService(selected_store, selected_client)
    app = FastAPI(title="Ollama Configurator Runtime Gateway")

    def authorize(request: Request) -> None:
        if api_key is None:
            return
        supplied = request.headers.get("x-api-key")
        if supplied is None:
            authorization = request.headers.get("authorization", "")
            supplied = authorization.removeprefix("Bearer ")
        if supplied != api_key:
            raise HTTPException(status_code=401, detail="gateway API key is required")

    @app.api_route("/", methods=["GET", "HEAD"])
    def ollama_probe() -> str:
        return "Ollama is running"

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "runtime-gateway"}

    @app.post("/api/generate")
    def generate(request: Request, payload: dict[str, Any]) -> Any:
        authorize(request)
        try:
            if payload.get("stream", False):
                return StreamingResponse(
                    (
                        json.dumps(chunk, ensure_ascii=False) + "\n"
                        for chunk in service.stream_generate(payload)
                    ),
                    media_type="application/x-ndjson",
                )
            return service.generate(payload)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/v1/chat/completions")
    def chat(request: Request, payload: dict[str, Any]) -> Any:
        authorize(request)
        try:
            if payload.get("stream", False):
                def events() -> Iterator[str]:
                    try:
                        for chunk in service.stream_chat(payload):
                            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                    except Exception as error:
                        error_payload = {
                            "error": {
                                "message": str(error),
                                "type": "server_error",
                            }
                        }
                        yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"

                return StreamingResponse(
                    events(),
                    media_type="text/event-stream",
                    headers={"Cache-Control": "no-cache"},
                )
            return service.chat(payload)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/api/chat")
    def ollama_chat(request: Request, payload: dict[str, Any]) -> Any:
        authorize(request)
        try:
            if payload.get("stream", False):
                return StreamingResponse(
                    (
                        json.dumps(chunk, ensure_ascii=False) + "\n"
                        for chunk in service.stream_chat_ollama(payload)
                    ),
                    media_type="application/x-ndjson",
                )
            return service.chat_ollama(payload)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/api/tags")
    def tags(request: Request) -> Any:
        authorize(request)
        return {"models": [model.model_dump() for model in selected_client.list_models()]}

    @app.get("/api/version")
    def version(request: Request) -> Any:
        authorize(request)
        result = selected_client.get_version()
        return result.model_dump() if hasattr(result, "model_dump") else result

    @app.post("/api/show")
    def show(request: Request, payload: dict[str, Any]) -> dict[str, Any]:
        authorize(request)
        # `ollama run` sends the model identifier as `name`, while other
        # Ollama-compatible clients commonly send `model`.
        model = payload.get("model", payload.get("name"))
        if not isinstance(model, str):
            raise HTTPException(status_code=400, detail="model must be a non-empty string")
        return selected_client.show_model(model)

    @app.get("/api/ps")
    def ps(request: Request) -> dict[str, Any]:
        authorize(request)
        return {"models": selected_client.list_running_models()}

    return app


app = create_gateway_app(api_key=os.getenv("OLLAMA_GATEWAY_API_KEY"))
