from pydantic import BaseModel

from backend.version import get_version


class AppSettings(BaseModel):
    app_name: str = "Ollama Configurator"
    version: str = get_version()
    host: str = "127.0.0.1"
    port: int = 8787


settings = AppSettings()
