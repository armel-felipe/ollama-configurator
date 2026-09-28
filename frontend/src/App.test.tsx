import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the application shell", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        ollama: { available: true, version: "0.5.7" },
        hardware: { os: "macos", architecture: "arm64" },
        models: [],
      }),
    }));
    render(<App />);

    return waitFor(() => {
      expect(screen.getByRole("heading", { name: /ollama configurator/i })).toBeInTheDocument();
    });
  });
});
