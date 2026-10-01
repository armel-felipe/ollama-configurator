from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.inference.service import InferenceService
from backend.ollama.client import OllamaError, get_ollama_client
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore

router = APIRouter(prefix="/api")


class InferenceRequest(BaseModel):
    prompt: str = Field(min_length=1)


class InferenceResponse(BaseModel):
    model: str
    requested_profile: dict[str, Any]
    thinking: str | None = None
    thinking_received: bool
    response: str
    runtime: dict[str, Any]


def get_inference_service() -> InferenceService:
    return InferenceService(ConfigStore(user_data_dir() / "config.json"), get_ollama_client())


@router.post("/models/{model_id}/inference-test", response_model=InferenceResponse)
def inference_test(model_id: str, request: InferenceRequest) -> InferenceResponse:
    try:
        result = get_inference_service().run(model_id, request.prompt)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except OllamaError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return InferenceResponse(model=model_id, **result.__dict__)
