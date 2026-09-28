from backend.hardware.detector import HardwareDetector


def test_detector_normalizes_macos_arm_hardware() -> None:
    snapshot = HardwareDetector(
        system_name="Darwin",
        machine_name="arm64",
        memory_bytes=36 * 1024**3,
        gpu_vendor="Apple",
    ).detect()

    assert snapshot.os == "macos"
    assert snapshot.architecture == "arm64"
    assert snapshot.memory_bytes == 36 * 1024**3
    assert snapshot.gpu_vendor == "apple"
    assert snapshot.backends == ["metal"]


def test_detector_uses_unknown_values_when_signals_are_unavailable(monkeypatch) -> None:
    def unavailable(_: str) -> int:
        raise ValueError("unavailable")

    monkeypatch.setattr("backend.hardware.detector.os.sysconf", unavailable)

    snapshot = HardwareDetector(
        system_name="UnknownOS",
        machine_name="unknown",
        memory_bytes=None,
        gpu_vendor=None,
    ).detect()

    assert snapshot.os == "unknown"
    assert snapshot.memory_bytes is None
    assert snapshot.gpu_vendor is None
    assert snapshot.backends == ["auto"]


def test_detector_reads_memory_from_posix_sysconf(monkeypatch) -> None:
    values = {"SC_PHYS_PAGES": 9, "SC_PAGE_SIZE": 4}
    monkeypatch.setattr("backend.hardware.detector.os.sysconf", values.__getitem__)

    snapshot = HardwareDetector("Linux", "x86_64", None, None).detect()

    assert snapshot.memory_bytes == 36
