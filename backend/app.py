from fastapi import FastAPI
from pydantic import BaseModel

from backend.api.diagnostics_routes import router as diagnostics_router
from backend.api.gateway_routes import router as gateway_router
from backend.api.inference_routes import router as inference_router
from backend.api.model_runtime_routes import router as model_runtime_router
from backend.api.model_settings_routes import router as model_settings_router
from backend.api.ollama_routes import router as ollama_router
from backend.api.reset_routes import router as reset_router
from backend.config import settings
from backend.logging_config import configure_logging

configure_logging()


class HealthResponse(BaseModel):
    status: str
    version: str


app = FastAPI(title=settings.app_name, version=settings.version)
app.include_router(ollama_router)
app.include_router(diagnostics_router)
app.include_router(gateway_router)
app.include_router(inference_router)
app.include_router(model_settings_router)
app.include_router(model_runtime_router)
app.include_router(reset_router)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.version)
