from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from pydantic import BaseModel

from backend.api.application_routes import router as application_router
from backend.api.diagnostics_routes import router as diagnostics_router
from backend.api.gateway_routes import router as gateway_router
from backend.api.inference_routes import router as inference_router
from backend.api.log_routes import router as log_router
from backend.api.model_runtime_routes import router as model_runtime_router
from backend.api.model_settings_routes import router as model_settings_router
from backend.api.ollama_routes import router as ollama_router
from backend.api.reset_routes import router as reset_router
from backend.api.server_settings_routes import router as server_settings_router
from backend.config import settings
from backend.gateway_manager import GatewayManagerError
from backend.api.gateway_routes import get_gateway_manager
from backend.logging_config import configure_logging

configure_logging()


class HealthResponse(BaseModel):
    status: str
    version: str



@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    gateway_manager = get_gateway_manager()
    try:
        gateway_manager.start()
    except GatewayManagerError:
        # A listener owned by another process remains visible as external in
        # the UI; the application itself must still start for recovery.
        pass
    try:
        yield
    finally:
        gateway_manager.stop()


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
app.include_router(ollama_router)
app.include_router(diagnostics_router)
app.include_router(application_router)
app.include_router(gateway_router)
app.include_router(inference_router)
app.include_router(log_router)
app.include_router(model_settings_router)
app.include_router(model_runtime_router)
app.include_router(reset_router)
app.include_router(server_settings_router)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.version)
