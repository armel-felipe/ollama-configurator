from backend.ollama.schemas import CapabilitiesResponse


def available_capabilities() -> CapabilitiesResponse:
    return CapabilitiesResponse(capabilities=["auto"])
