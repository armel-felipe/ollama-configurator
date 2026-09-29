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

  it("presents context presets as one selectable group", async () => {
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { num_ctx: 32768 } })}
        saveSettings={vi.fn().mockResolvedValue({ options: {} })}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByRole("radiogroup", { name: /context window/i })).toBeInTheDocument());
    expect(screen.getByRole("radio", { name: "32K" })).toBeChecked();
    fireEvent.click(screen.getByRole("radio", { name: "64K" }));
    expect(screen.getByRole("radio", { name: "64K" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "32K" })).not.toBeChecked();
  });

  it("keeps boolean thinking as an explicit accessible switch", async () => {
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { think: false }, thinking: { values: [false, true], default: true } })}
        saveSettings={vi.fn().mockResolvedValue({ options: { think: false } })}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByRole("checkbox", { name: /thinking/i })).toBeInTheDocument());
    expect(screen.getByRole("checkbox", { name: /thinking/i })).not.toBeChecked();
    fireEvent.click(screen.getByRole("checkbox", { name: /thinking/i }));
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(/configurações salvas/i));
  });

  it("persists Default instead of the previous custom value", async () => {
    const save = vi.fn().mockResolvedValue({ options: {} });
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { num_ctx: 32768 }, defaults: { num_ctx: "Ollama Default" } })}
        saveSettings={save}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByLabelText("Context Window", { exact: true })).toHaveValue(32768));
    fireEvent.click(screen.getByRole("button", { name: "Context Window Ollama Default" }));
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => expect(save).toHaveBeenCalledWith(expect.objectContaining({ num_ctx: "default" })));
  });

  it("marks the screen as having unsaved changes after a successful save", async () => {
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { temperature: 0.7 } })}
        saveSettings={vi.fn().mockResolvedValue({ options: { temperature: 0.2 } })}
        applySettings={vi.fn().mockResolvedValue({ applied: true })}
      />,
    );

    await waitFor(() => expect(screen.getByLabelText("Temperature", { exact: true })).toHaveValue(0.7));
    fireEvent.change(screen.getByLabelText("Temperature", { exact: true }), { target: { value: "0.2" } });
    expect(screen.getByRole("status")).toHaveTextContent("Alterações não salvas");
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Configurações salvas"));

    fireEvent.change(screen.getByLabelText("Temperature", { exact: true }), { target: { value: "0.3" } });
    expect(screen.getByRole("status")).toHaveTextContent("Alterações não salvas");
  });

  it("shows the runtime confirmation after applying saved settings", async () => {
    const apply = vi.fn().mockResolvedValue({
      applied: true,
      runtime: { loaded: true, context: 16384, applied_options: { num_ctx: 16384 } },
    });
    const published: Array<{ runtime: boolean; dirty: boolean }> = [];
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: {} })}
        saveSettings={vi.fn().mockResolvedValue({ options: {} })}
        applySettings={apply}
        onStateChange={(next) => published.push({ runtime: Boolean(next.runtime), dirty: next.dirty })}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: /aplicar/i })).toBeEnabled());
    fireEvent.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Runtime confirmado: 16K"));
    expect(published.at(-1)).toMatchObject({ runtime: true, dirty: false });
    expect(apply).toHaveBeenCalledTimes(1);
  });

  it("does not claim success when the effective context differs", async () => {
    const apply = vi.fn().mockResolvedValue({
      applied: false,
      runtime: {
        loaded: true,
        context: 131072,
        requested_context: 65536,
        context_matches: false,
        applied_options: { num_ctx: 65536 },
      },
    });
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: { num_ctx: 65536 } })}
        saveSettings={vi.fn().mockResolvedValue({ options: { num_ctx: 65536 } })}
        applySettings={apply}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: /aplicar/i })).toBeEnabled());
    fireEvent.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent(/solicitado 64K, efetivo 128K/i),
    );
    expect(screen.queryByText(/Runtime confirmado/)).not.toBeInTheDocument();
  });

  it("requires saving before applying a changed profile", async () => {
    const apply = vi.fn().mockResolvedValue({ applied: true });
    render(
      <ModelSettingsPage
        modelId="qwen:latest"
        loadSettings={async () => ({ options: {} })}
        saveSettings={vi.fn().mockResolvedValue({ options: {} })}
        applySettings={apply}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: /personalizar temperature/i })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /personalizar temperature/i }));
    fireEvent.click(screen.getByRole("button", { name: /aplicar/i }));

    expect(apply).not.toHaveBeenCalled();
    expect(screen.getByRole("status")).toHaveTextContent("Salve as alterações antes de aplicar");
  });
});
