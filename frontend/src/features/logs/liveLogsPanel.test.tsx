import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { LiveLogsPanel, type LogEvent } from "./LiveLogsPanel";

afterEach(cleanup);

const event: LogEvent = {
  timestamp: "2026-09-29T20:00:00.000Z",
  service: "gateway",
  level: "info",
  message: "Perfil aplicado à requisição",
  metadata: { model: "qwen3.8:27b-mlx", think: false, num_ctx: 16384 },
};

test("shows recent events, metadata and live connection state", async () => {
  const subscribe = vi.fn((_onEvent, onConnection) => { onConnection(true); return () => undefined; });
  render(<LiveLogsPanel load={() => Promise.resolve([event])} subscribe={subscribe} />);

  expect(await screen.findByText(/Perfil aplicado/)).toBeInTheDocument();
  expect(screen.getByText(/think=false/)).toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent("Ao vivo");
});

test("filters events by service and clears the visible list", async () => {
  const ollamaEvent = { ...event, service: "ollama" as const, message: "Modelo carregado" };
  render(<LiveLogsPanel load={() => Promise.resolve([event, ollamaEvent])} subscribe={() => () => undefined} />);

  await screen.findByText(/Modelo carregado/);
  fireEvent.click(screen.getByRole("button", { name: "Gateway" }));
  expect(screen.getByText(/Perfil aplicado/)).toBeInTheDocument();
  expect(screen.queryByText("Modelo carregado")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Limpar visualização" }));
  await waitFor(() => expect(screen.getByText("Aguardando eventos…")).toBeInTheDocument());
});
