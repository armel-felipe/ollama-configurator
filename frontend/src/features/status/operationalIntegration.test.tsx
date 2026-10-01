import { render, screen } from "@testing-library/react";
import { useEffect } from "react";
import { describe, expect, it, vi } from "vitest";
import { DiagnosticsPage } from "../diagnostics/DiagnosticsPage";

vi.mock("../server/ServerSettingsPage", () => ({
  ServerSettingsPage: ({ onStateChange }: { onStateChange: (state: { loaded: boolean; available: boolean; pendingRestart: boolean; dirty: boolean; error: string | null }) => void }) => {
    useEffect(() => onStateChange({ loaded: true, available: true, pendingRestart: true, dirty: false, error: null }), [onStateChange]);
    return <div />;
  },
}));

vi.mock("../gateway/GatewayControls", () => ({
  GatewayControls: ({ onStateChange }: { onStateChange: (status: { state: "running"; host: string; port: number }, error: string | null) => void }) => {
    useEffect(() => onStateChange({ state: "running", host: "127.0.0.1", port: 11435 }, null), [onStateChange]);
    return <div />;
  },
}));

describe("operational status integration", () => {
  it("surfaces a pending server state and its next action above the settings", async () => {
    render(
      <DiagnosticsPage
        loadDiagnostics={async () => ({
          application_version: "0.1.10",
          ollama: { available: true, version: "0.40.0" },
          hardware: { os: "macos", architecture: "arm64" },
          models: [],
        })}
      />,
    );

    expect(await screen.findByText("Aplicação pendente")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Aplicar no Ollama" })).toBeInTheDocument();
  });
});
