import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ConnectionsPage } from "./ConnectionsPage";

const gateway = { state: "stopped" as const, host: "127.0.0.1", port: 11435 };
const models = [{ name: "qwen3.8:27b-mlx" }, { name: "gemma4:26b-mlx" }];

describe("ConnectionsPage", () => {
  afterEach(() => cleanup());

  it("renders all fifteen client cards and explains when no model is selected", () => {
    const { container } = render(<ConnectionsPage models={models} selectedModel={undefined} gateway={gateway} onSelectModel={() => undefined} />);

    expect(screen.getByRole("heading", { name: /conectar seus clientes/i })).toBeInTheDocument();
    expect(within(screen.getByRole("group", { name: /clientes ollama/i })).getAllByRole("button")).toHaveLength(15);
    expect(container.querySelectorAll(".connection-card [data-brand-icon]")).toHaveLength(15);
    expect(screen.getByText(/selecione um modelo antes de copiar/i)).toBeInTheDocument();
  });

  it("copies the selected client's command immediately", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<ConnectionsPage models={models} selectedModel={models[0].name} gateway={gateway} onSelectModel={() => undefined} />);

    fireEvent.click(screen.getByRole("button", { name: /opencode/i }));
    await waitFor(() => expect(writeText).toHaveBeenCalledWith("export OLLAMA_HOST=http://127.0.0.1:11435\nollama launch opencode --model qwen3.8:27b-mlx"));
    expect(screen.getByText(/comando do opencode copiado/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/shell/i), { target: { value: "powershell" } });
    fireEvent.click(screen.getByRole("button", { name: /opencode/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith('$env:OLLAMA_HOST="http://127.0.0.1:11435"\nollama launch opencode --model qwen3.8:27b-mlx'));
  });

  it("shows the stopped gateway recovery message and copies the terminal command", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<ConnectionsPage models={models} selectedModel={models[0].name} gateway={gateway} onSelectModel={() => undefined} />);

    fireEvent.click(within(screen.getByRole("group", { name: /clientes ollama/i })).getByRole("button", { name: /^terminal executar/i }));
    expect(screen.getByText(/gateway parada/i)).toBeInTheDocument();
    expect(screen.queryByText(/comando de conexão/i)).not.toBeInTheDocument();
    expect(writeText).toHaveBeenCalledWith("export OLLAMA_HOST=http://127.0.0.1:11435\nollama run qwen3.8:27b-mlx --verbose");
    await waitFor(() => expect(screen.getByText(/comando do terminal copiado/i)).toBeInTheDocument());
  });
});
