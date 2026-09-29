import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { GatewayControls } from "./GatewayControls";

describe("GatewayControls", () => {
  afterEach(() => {
    vi.useRealTimers();
    cleanup();
  });

  it("shows the start button for a stopped gateway and starts it", async () => {
    const start = vi.fn().mockResolvedValue({ state: "running", host: "127.0.0.1", port: 11435, pid: 7 });
    render(
      <GatewayControls
        getStatus={async () => ({ state: "stopped", host: "127.0.0.1", port: 11435 })}
        start={start}
        stop={vi.fn()}
        restart={vi.fn()}
      />,
    );

    await waitFor(() => expect(screen.getByRole("button", { name: "Iniciar servidor" })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Iniciar servidor" }));

    await waitFor(() => expect(start).toHaveBeenCalledTimes(1));
    expect(await screen.findByText("Ativo — respondendo")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Parar servidor" })).toBeInTheDocument();
  });

  it("reports an unmanaged listener instead of offering to kill it", async () => {
    const published: string[] = [];
    render(
      <GatewayControls
        getStatus={async () => ({ state: "external", host: "127.0.0.1", port: 11435, detail: "processo externo" })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
        onStateChange={(status) => published.push(status.state)}
      />,
    );

    expect(await screen.findByText(/Outro processo está usando a porta/)).toBeInTheDocument();
    expect(published).toContain("external");
    expect(screen.queryByRole("button", { name: "Parar servidor" })).not.toBeInTheDocument();
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
      />,
    );

    await act(async () => { await Promise.resolve(); });
    expect(screen.getByText("Ativo — respondendo")).toBeInTheDocument();

    await act(async () => { vi.advanceTimersByTime(5000); });
    expect(getStatus).toHaveBeenCalledTimes(2);
  });
});
