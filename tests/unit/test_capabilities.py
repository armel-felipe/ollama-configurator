from backend.domain.capabilities import CapabilityContext, filter_capabilities


def test_apple_context_exposes_metal_only() -> None:
    capabilities = filter_capabilities(
        ["auto", "metal", "cuda", "rocm", "vulkan"],
        CapabilityContext(os="macos", architecture="arm64", gpu_vendor="apple"),
    )

    assert capabilities == ["auto", "metal"]


def test_nvidia_context_exposes_cuda_and_vulkan() -> None:
    capabilities = filter_capabilities(
        ["auto", "metal", "cuda", "rocm", "vulkan"],
        CapabilityContext(os="windows", architecture="x64", gpu_vendor="nvidia"),
    )

    assert capabilities == ["auto", "cuda", "vulkan"]
