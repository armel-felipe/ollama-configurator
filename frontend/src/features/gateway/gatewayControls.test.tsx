import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { GatewayControls } from "./GatewayControls";

describe("GatewayControls", () => {
  afterEach(() => cleanup());

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
    expect(await screen.findByText("Ativo")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Parar servidor" })).toBeInTheDocument();
  });

  it("reports an unmanaged listener instead of offering to kill it", async () => {
    render(
      <GatewayControls
        getStatus={async () => ({ state: "external", host: "127.0.0.1", port: 11435, detail: "processo externo" })}
        start={vi.fn()}
        stop={vi.fn()}
        restart={vi.fn()}
      />,
    );

    expect(await screen.findByText(/Outro processo está usando a porta/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Parar servidor" })).not.toBeInTheDocument();
  });
});
