import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DiagnosticsPage } from "./DiagnosticsPage";

vi.mock("../models/ModelSettingsPage", () => ({
  ModelSettingsPage: () => <div />,
}));

describe("DiagnosticsPage", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => cleanup());

  it("restores the selected model after the page is reloaded", async () => {
    localStorage.setItem("ollama-configurator.selected-model", "qwen3.6:35b-a3b-nvfp4");

    render(
      <DiagnosticsPage
        loadDiagnostics={async () => ({
          application_version: "0.1.10",
          ollama: { available: true, version: "0.5.7" },
          hardware: { os: "macos", architecture: "arm64" },
          models: [{ name: "qwen3.6:35b-a3b-nvfp4" }],
        })}
      />,
    );

    expect(await screen.findByRole("button", { name: "qwen3.6:35b-a3b-nvfp4" })).toHaveAttribute("aria-pressed", "true");
  });

  it("shows hardware and models after loading", async () => {
    render(
      <DiagnosticsPage
        loadDiagnostics={async () => ({
          application_version: "0.1.10",
          ollama: { available: true, version: "0.5.7" },
          hardware: { os: "macos", architecture: "arm64", memoryBytes: 36 * 1024 ** 3 },
          models: [{ name: "qwen:latest", size: 123 }],
        })}
      />,
    );

    expect(screen.getAllByText(/carregando/i).length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.getAllByText("qwen:latest").length).toBeGreaterThan(0));
    expect(screen.getByText(/ollama 0\.5\.7/i)).toBeInTheDocument();
    expect(screen.getAllByText(/macos/i).length).toBeGreaterThan(0);
  });

  it("shows an actionable error when discovery fails", async () => {
    render(<DiagnosticsPage loadDiagnostics={async () => { throw new Error("Ollama indisponível"); }} />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/indisponível/i));
    expect(screen.getByRole("button", { name: /tentar novamente/i })).toBeInTheDocument();
  });
});
