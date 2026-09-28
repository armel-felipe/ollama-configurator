import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ModelSettingsPage } from "./ModelSettingsPage";

describe("ModelSettingsPage", () => {
  afterEach(() => cleanup());

  it("loads and saves basic model options", async () => {
    const save = vi.fn().mockResolvedValue({ options: { temperature: 0.2 } });
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { temperature: 0.7, num_ctx: 32768 } })}
        saveSettings={save}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByLabelText("Temperature", { exact: true })).toHaveValue(0.7));
    fireEvent.change(screen.getByLabelText("Temperature", { exact: true }), { target: { value: "0.2" } });
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => expect(save).toHaveBeenCalledWith({
      temperature: 0.2,
      num_ctx: 32768,
      num_predict: "default",
      keep_alive: "default",
    }));
  });

  it("allows returning a parameter to Ollama Default", async () => {
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { temperature: 0.7 } })}
        saveSettings={vi.fn().mockResolvedValue({ options: {} })}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByLabelText("Temperature", { exact: true })).toHaveValue(0.7));
    fireEvent.click(screen.getByRole("button", { name: "Temperature Ollama Default" }));

    expect(screen.getByLabelText("Temperature", { exact: true })).toBeDisabled();
  });

  it("allows enabling a parameter that starts at Ollama Default", async () => {
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: {} })}
        saveSettings={vi.fn().mockResolvedValue({ options: {} })}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: "Personalizar Temperature" })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Personalizar Temperature" }));

    expect(screen.getByLabelText("Temperature", { exact: true })).not.toBeDisabled();
  });
});
