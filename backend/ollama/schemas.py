from pydantic import BaseModel, Field


class OllamaVersion(BaseModel):
    version: str


class OllamaModel(BaseModel):
    name: str
    size: int | None = None
    details: dict[str, object] = Field(default_factory=dict)


class ModelsResponse(BaseModel):
    models: list[OllamaModel]


class OllamaStatusResponse(BaseModel):
    available: bool
    version: str | None = None
    error: str | None = None


class CapabilitiesResponse(BaseModel):
    capabilities: list[str]
