import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ComponentProps } from "react";
import { ConnectionsPage } from "./ConnectionsPage";

const gateway = { state: "stopped" as const, host: "127.0.0.1", port: 11435 };
const models = [{ name: "qwen3.8:27b-mlx" }, { name: "gemma4:26b-mlx" }];
const defaultSettings = { host: "127.0.0.1", effective_host: "127.0.0.1", port: 11435, pending_restart: false, options: [], tailscale_ip: null };

function renderConnections(overrides: Partial<ComponentProps<typeof ConnectionsPage>> = {}) {
  return render(<ConnectionsPage
    models={models}
    selectedModel={models[0].name}
    gateway={gateway}
    onSelectModel={() => undefined}
    loadGatewaySettings={vi.fn().mockResolvedValue(defaultSettings)}
    saveTailscaleIp={vi.fn().mockResolvedValue(defaultSettings)}
    {...overrides}
  />);
}

describe("ConnectionsPage", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("defaults to PowerShell on Windows and keeps the manual override", async () => {
    vi.spyOn(window.navigator, "userAgent", "get").mockReturnValue("Mozilla/5.0 (Windows NT 10.0; Win64; x64)");
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    renderConnections();

    expect(screen.getByLabelText(/shell/i)).toHaveValue("powershell");
    fireEvent.click(screen.getByRole("button", { name: /opencode/i }));
    await waitFor(() => expect(writeText).toHaveBeenCalledWith('$env:OLLAMA_HOST="http://127.0.0.1:11435"\nollama launch opencode --model qwen3.8:27b-mlx'));
    fireEvent.change(screen.getByLabelText(/shell/i), { target: { value: "posix" } });
    fireEvent.click(screen.getByRole("button", { name: /opencode/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://127.0.0.1:11435\nollama launch opencode --model qwen3.8:27b-mlx"));
  });

  it("renders all fifteen client cards and explains when no model is selected", () => {
    const { container } = renderConnections({ selectedModel: undefined });

    expect(screen.getByRole("heading", { name: /conectar seus clientes/i })).toBeInTheDocument();
    expect(within(screen.getByRole("group", { name: /clientes ollama/i })).getAllByRole("button")).toHaveLength(15);
    expect(container.querySelectorAll(".connection-card [data-brand-icon]")).toHaveLength(15);
    expect(screen.getByText(/selecione um modelo antes de copiar/i)).toBeInTheDocument();
  });

  it("copies the selected client's command immediately", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    renderConnections();

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
    renderConnections();

    fireEvent.click(within(screen.getByRole("group", { name: /clientes ollama/i })).getByRole("button", { name: /^terminal executar/i }));
    expect(screen.getByText(/gateway parada/i)).toBeInTheDocument();
    expect(screen.queryByText(/comando de conexão/i)).not.toBeInTheDocument();
    expect(writeText).toHaveBeenCalledWith("export OLLAMA_HOST=http://127.0.0.1:11435\nollama run qwen3.8:27b-mlx --verbose");
    await waitFor(() => expect(screen.getByText(/comando do terminal copiado/i)).toBeInTheDocument());
  });

  it("loads the persisted IP and uses it for macOS and Windows commands", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    const settings = { ...defaultSettings, host: "0.0.0.0", effective_host: "0.0.0.0", tailscale_ip: "100.87.71.48" };
    renderConnections({
      gateway: { state: "running", host: "0.0.0.0", port: 11435 },
      loadGatewaySettings: vi.fn().mockResolvedValue(settings),
    });

    expect(await screen.findByLabelText(/IP Tailscale da máquina servidora/i)).toHaveValue("100.87.71.48");
    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://100.87.71.48:11435\nollama run qwen3.8:27b-mlx --verbose"));

    fireEvent.change(screen.getByLabelText(/shell/i), { target: { value: "powershell" } });
    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith('$env:OLLAMA_HOST="http://100.87.71.48:11435"\nollama run qwen3.8:27b-mlx --verbose'));
  });

  it("uses the persisted save response for the next copied command", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    const saveTailscaleIp = vi.fn().mockResolvedValue({ ...defaultSettings, host: "0.0.0.0", effective_host: "0.0.0.0", tailscale_ip: "100.64.0.23" });
    renderConnections({
      gateway: { state: "running", host: "0.0.0.0", port: 11435 },
      loadGatewaySettings: vi.fn().mockResolvedValue({ ...defaultSettings, host: "0.0.0.0", effective_host: "0.0.0.0" }),
      saveTailscaleIp,
    });

    const input = await screen.findByLabelText(/IP Tailscale da máquina servidora/i);
    fireEvent.change(input, { target: { value: " 100.64.0.22 " } });
    fireEvent.click(screen.getByRole("button", { name: /salvar IP/i }));

    await waitFor(() => expect(saveTailscaleIp).toHaveBeenCalledWith("100.64.0.22"));
    expect(await screen.findByText(/IP Tailscale salvo/i)).toBeInTheDocument();
    expect(input).toHaveValue("100.64.0.23");

    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://100.64.0.23:11435\nollama run qwen3.8:27b-mlx --verbose"));
  });

  it("blocks copying until a Tailscale IP has been saved", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    renderConnections({
      gateway: { state: "running", host: "0.0.0.0", port: 11435 },
      loadGatewaySettings: vi.fn().mockResolvedValue({ ...defaultSettings, host: "0.0.0.0", effective_host: "0.0.0.0" }),
      saveTailscaleIp: vi.fn().mockResolvedValue(defaultSettings),
    });

    const input = await screen.findByLabelText(/IP Tailscale da máquina servidora/i);
    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));

    expect(writeText).not.toHaveBeenCalled();
    expect(await screen.findByText("Informe e salve o IP Tailscale antes de copiar o comando.")).toBeInTheDocument();
    expect(input).toHaveFocus();
  });

  it("never copies an unsaved draft and retains the saved IP after a failed save", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    const saveTailscaleIp = vi.fn().mockRejectedValue(new Error("IP inválido"));
    renderConnections({
      gateway: { state: "running", host: "0.0.0.0", port: 11435 },
      loadGatewaySettings: vi.fn().mockResolvedValue({ ...defaultSettings, host: "0.0.0.0", effective_host: "0.0.0.0", tailscale_ip: "100.64.0.10" }),
      saveTailscaleIp,
    });

    const input = await screen.findByLabelText(/IP Tailscale da máquina servidora/i);
    fireEvent.change(input, { target: { value: "100.64.0.99" } });
    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://100.64.0.10:11435\nollama run qwen3.8:27b-mlx --verbose"));

    fireEvent.click(screen.getByRole("button", { name: /salvar IP/i }));
    expect(await screen.findByText("IP inválido")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
    await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://100.64.0.10:11435\nollama run qwen3.8:27b-mlx --verbose"));
  });
});
