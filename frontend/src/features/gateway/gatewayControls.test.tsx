import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { GatewayControls } from "./GatewayControls";

describe("GatewayControls", () => {
  afterEach(() => {
    vi.useRealTimers();
    cleanup();
  });

  it("shows one clearly named gateway start button for a stopped gateway", async () => {
    const start = vi.fn().mockResolvedValue({ state: "running", host: "127.0.0.1", port: 11435, pid: 7 });
    render(
      <GatewayControls
        getStatus={async () => ({ state: "stopped", host: "127.0.0.1", port: 11435 })}
        start={start}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={vi.fn()}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: "Iniciar gateway" })).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: "Iniciar servidor" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Iniciar gateway" }));

    await waitFor(() => expect(start).toHaveBeenCalledTimes(1));
    expect(await screen.findByText("Ativo — respondendo")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Parar gateway" })).toBeInTheDocument();
  });

  it("reports an unmanaged listener and offers a confirmed release", async () => {
    const published: string[] = [];
    const releaseExternal = vi.fn().mockResolvedValue({ state: "stopped", host: "127.0.0.1", port: 11435 });
    render(
      <GatewayControls
        getStatus={async () => ({ state: "external", host: "127.0.0.1", port: 11435, detail: "processo externo" })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={releaseExternal}
        onStateChange={(status) => published.push(status.state)}
      />,
    );

    expect(await screen.findByText(/processo externo.*está usando a porta/)).toBeInTheDocument();
    expect(published).toContain("external");
    expect(screen.queryByRole("button", { name: "Parar gateway" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Liberar porta" }));
    fireEvent.click(screen.getByRole("button", { name: "Confirmar encerramento" }));
    await waitFor(() => expect(releaseExternal).toHaveBeenCalledTimes(1));
  });

  it("keeps checking a running gateway and labels it as responding", async () => {
    vi.useFakeTimers();
    const getStatus = vi.fn().mockResolvedValue({
      state: "running",
      host: "127.0.0.1",
      port: 11435,
      pid: 7,
    });

    render(
      <GatewayControls
        getStatus={getStatus}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={vi.fn()}
      />,
    );

    await act(async () => { await Promise.resolve(); });
    expect(screen.getByText("Ativo — respondendo")).toBeInTheDocument();

    await act(async () => { vi.advanceTimersByTime(5000); });
    expect(getStatus).toHaveBeenCalledTimes(2);
  });

  it("shows the two bind options and warns before network exposure", async () => {
    render(
      <GatewayControls
        getStatus={async () => ({ state: "running", host: "127.0.0.1", port: 11435, pid: 7 })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={vi.fn()}
        getSettings={async () => ({
          host: "127.0.0.1",
          effective_host: "127.0.0.1",
          port: 11435,
          pending_restart: false,
          options: ["127.0.0.1", "0.0.0.0"],
          warning: null,
        })}
        updateSettings={vi.fn()}
        applySettings={vi.fn()}
      />,
    );

    await screen.findByLabelText("Endereço de escuta do gateway");
    expect(screen.getByRole("option", { name: "Somente esta máquina (127.0.0.1)" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Rede local e Tailscale (0.0.0.0)" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Endereço de escuta do gateway"), { target: { value: "0.0.0.0" } });

    expect(await screen.findByRole("alert")).toHaveTextContent(/interfaces de rede/i);
    expect(screen.getByText("Alteração não salva")).toBeInTheDocument();
  });

  it("saves the selected bind and applies it only after explicit gateway restart", async () => {
    const updateSettings = vi.fn().mockResolvedValue({
      host: "0.0.0.0",
      effective_host: "127.0.0.1",
      port: 11435,
      pending_restart: true,
      options: ["127.0.0.1", "0.0.0.0"],
      warning: "aviso",
    });
    const applySettings = vi.fn().mockResolvedValue({
      status: { state: "starting", host: "0.0.0.0", port: 11435, pid: 8 },
      settings: {
        host: "0.0.0.0",
        effective_host: "0.0.0.0",
        port: 11435,
        pending_restart: false,
        options: ["127.0.0.1", "0.0.0.0"],
        warning: "aviso",
      },
    });
    render(
      <GatewayControls
        getStatus={async () => ({ state: "running", host: "127.0.0.1", port: 11435, pid: 7 })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={vi.fn()}
        getSettings={async () => ({
          host: "127.0.0.1",
          effective_host: "127.0.0.1",
          port: 11435,
          pending_restart: false,
          options: ["127.0.0.1", "0.0.0.0"],
          warning: null,
        })}
        updateSettings={updateSettings}
        applySettings={applySettings}
      />,
    );

    await screen.findByLabelText("Endereço de escuta do gateway");
    fireEvent.change(screen.getByLabelText("Endereço de escuta do gateway"), { target: { value: "0.0.0.0" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar endereço" }));
    await waitFor(() => expect(updateSettings).toHaveBeenCalledWith("0.0.0.0"));
    expect(screen.getByRole("button", { name: "Aplicar e reiniciar gateway" })).toBeEnabled();
    fireEvent.click(screen.getByRole("button", { name: "Aplicar e reiniciar gateway" }));
    await waitFor(() => expect(applySettings).toHaveBeenCalledTimes(1));
    expect(await screen.findByText(/Gateway reiniciando/i)).toBeInTheDocument();
  });

  it("keeps gateway settings actionable when loading fails", async () => {
    render(
      <GatewayControls
        getStatus={async () => ({ state: "running", host: "127.0.0.1", port: 11435, pid: 7 })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        releaseExternal={vi.fn()}
        getSettings={async () => { throw new Error("Não foi possível carregar o bind"); }}
        updateSettings={vi.fn()}
        applySettings={vi.fn()}
      />,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(/carregar o bind/i);
    expect(screen.getByRole("button", { name: "Recarregar acesso do gateway" })).toBeInTheDocument();
  });
});
