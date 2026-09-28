from pydantic import BaseModel


class HardwareSnapshot(BaseModel):
    os: str
    architecture: str
    cpu: str | None = None
    memory_bytes: int | None = None
    gpu_vendor: str | None = None
    backends: list[str]
