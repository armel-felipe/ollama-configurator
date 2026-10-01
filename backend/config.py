from pydantic import BaseModel


class AppSettings(BaseModel):
    app_name: str = "Ollama Configurator"
    version: str = "0.1.8"
    host: str = "127.0.0.1"
    port: int = 8787


settings = AppSettings()
