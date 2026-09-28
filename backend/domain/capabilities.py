from pydantic import BaseModel


class CapabilityContext(BaseModel):
    os: str
    architecture: str
    gpu_vendor: str | None = None


def filter_capabilities(
    capabilities: list[str], context: CapabilityContext
) -> list[str]:
    allowed = {"auto"}
    if context.gpu_vendor == "apple" and context.os == "macos":
        allowed.add("metal")
    if context.gpu_vendor == "nvidia":
        allowed.update({"cuda", "vulkan"})
    if context.gpu_vendor == "amd":
        allowed.update({"rocm", "vulkan"})
    return [capability for capability in capabilities if capability in allowed]
