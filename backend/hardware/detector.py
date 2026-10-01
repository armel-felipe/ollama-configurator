import os
import platform

from backend.hardware.schemas import HardwareSnapshot


class HardwareDetector:
    def __init__(
        self,
        system_name: str | None = None,
        machine_name: str | None = None,
        memory_bytes: int | None = None,
        gpu_vendor: str | None = None,
    ) -> None:
        self.system_name = system_name or platform.system()
        self.machine_name = machine_name or platform.machine()
        self.memory_bytes = memory_bytes if memory_bytes is not None else self._memory_bytes()
        self.gpu_vendor = self._normalize_gpu(gpu_vendor)

    def detect(self) -> HardwareSnapshot:
        normalized_os = {"Darwin": "macos", "Windows": "windows"}.get(
            self.system_name, "unknown"
        )
        gpu_vendor = self.gpu_vendor
        if gpu_vendor is None and normalized_os == "macos" and self.machine_name == "arm64":
            gpu_vendor = "apple"
        return HardwareSnapshot(
            os=normalized_os,
            architecture=self.machine_name,
            cpu=platform.processor() or None,
            memory_bytes=self.memory_bytes,
            gpu_vendor=gpu_vendor,
            backends=self._backends(normalized_os, gpu_vendor),
        )

    def _memory_bytes(self) -> int | None:
        if hasattr(os, "sysconf"):
            try:
                return int(os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"))
            except (ValueError, OSError):
                return None
        return None

    @staticmethod
    def _normalize_gpu(gpu_vendor: str | None) -> str | None:
        return gpu_vendor.lower() if gpu_vendor else None

    @staticmethod
    def _backends(os_name: str, gpu_vendor: str | None) -> list[str]:
        if os_name == "macos" and gpu_vendor == "apple":
            return ["metal"]
        if gpu_vendor == "nvidia":
            return ["cuda", "vulkan"]
        if gpu_vendor == "amd":
            return ["rocm", "vulkan"]
        return ["auto"]


def get_hardware_detector() -> HardwareDetector:
    return HardwareDetector()
