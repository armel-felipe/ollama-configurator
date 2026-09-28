import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiagnosticsPage } from "./DiagnosticsPage";

describe("DiagnosticsPage", () => {
  it("shows hardware and models after loading", async () => {
    render(
      <DiagnosticsPage
        loadDiagnostics={async () => ({
          ollama: { available: true, version: "0.5.7" },
          hardware: { os: "macos", architecture: "arm64", memoryBytes: 36 * 1024 ** 3 },
          models: [{ name: "qwen:latest", size: 123 }],
        })}
      />,
    );

    expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("qwen:latest")).toBeInTheDocument());
    expect(screen.getByText(/ollama 0\.5\.7/i)).toBeInTheDocument();
    expect(screen.getByText(/macos/i)).toBeInTheDocument();
  });

  it("shows an actionable error when discovery fails", async () => {
    render(<DiagnosticsPage loadDiagnostics={async () => { throw new Error("Ollama indisponível"); }} />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/indisponível/i));
    expect(screen.getByRole("button", { name: /tentar novamente/i })).toBeInTheDocument();
  });
});
