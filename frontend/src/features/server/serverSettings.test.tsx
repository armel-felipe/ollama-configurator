import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import type { ServerSettingsState } from "../../api/client";
import { ServerSettingsPage } from "./ServerSettingsPage";

afterEach(cleanup);

const state: ServerSettingsState = {
  settings: {},
  effective: { OLLAMA_KV_CACHE_TYPE: "f16" },
  pending_restart: false,
  available: true,
  capabilities: {
    OLLAMA_KV_CACHE_TYPE: {
      label: "KV cache",
      description: "Tipo de quantização do cache de atenção",
      type: "select",
      options: ["f16", "q8_0", "q4_0"],
      default: "f16",
    },
  },
};

const contextState: ServerSettingsState = {
  settings: {},
  effective: { OLLAMA_CONTEXT_LENGTH: 4096 },
  pending_restart: false,
  available: true,
  capabilities: {
    OLLAMA_CONTEXT_LENGTH: {
      label: "Contexto global",
      description: "Limite padrão",
      type: "number",
      default: 4096,
      min: 1,
      presets: [
        { label: "16K", value: 16384 },
        { label: "32K", value: 32768 },
        { label: "64K", value: 65536 },
        { label: "128K", value: 131072 },
        { label: "256K", value: 262144 },
      ],
    },
  },
};

test("shows global settings before model selection and exposes restart-pending state", async () => {
  const update = vi.fn().mockResolvedValue({ ...state, pending_restart: true, settings: { OLLAMA_KV_CACHE_TYPE: "q8_0" } });
  const restart = vi.fn().mockResolvedValue({ success: true, detail: "ok", reapplied_models: [] });
  render(<ServerSettingsPage load={() => Promise.resolve(state)} update={update} restart={restart} reset={() => Promise.resolve(state)} restartApplication={vi.fn()} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  expect(screen.getByLabelText("KV cache")).toHaveValue("f16");
  fireEvent.change(screen.getByLabelText("KV cache"), { target: { value: "q8_0" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));

  await waitFor(() => expect(update).toHaveBeenCalledWith({ OLLAMA_KV_CACHE_TYPE: "q8_0" }));
  expect(await screen.findByRole("status")).toHaveTextContent(/aguardando aplicação/i);
});

test("restart action reports model profile reapplication", async () => {
  const restart = vi.fn().mockResolvedValue({ success: true, detail: "ok", reapplied_models: ["gemma4:26b-mlx"] });
  render(<ServerSettingsPage load={() => Promise.resolve({ ...state, pending_restart: true })} update={vi.fn()} restart={restart} reset={() => Promise.resolve(state)} restartApplication={vi.fn()} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  fireEvent.click(screen.getByRole("button", { name: "Aplicar alterações no Ollama" }));
  fireEvent.click(screen.getByRole("button", { name: "Confirmar aplicação" }));

  await waitFor(() => expect(restart).toHaveBeenCalledTimes(1));
  expect(await screen.findByText(/perfis reaplicados/i)).toBeInTheDocument();
});

test("offers context window presets for the global context", async () => {
  const update = vi.fn().mockResolvedValue({ ...contextState, pending_restart: true });
  render(<ServerSettingsPage load={() => Promise.resolve(contextState)} update={update} restart={vi.fn()} reset={() => Promise.resolve(contextState)} restartApplication={vi.fn()} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  fireEvent.click(screen.getByRole("radio", { name: "32K" }));
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));

  await waitFor(() => expect(update).toHaveBeenCalledWith({ OLLAMA_CONTEXT_LENGTH: 32768 }));
});

test("publishes dirty and pending states to the workspace", async () => {
  const published: Array<{ dirty: boolean; pendingRestart: boolean }> = [];
  const update = vi.fn().mockResolvedValue({ ...state, pending_restart: true, settings: { OLLAMA_KV_CACHE_TYPE: "q8_0" } });
  render(<ServerSettingsPage load={() => Promise.resolve(state)} update={update} restart={vi.fn()} reset={() => Promise.resolve(state)} restartApplication={vi.fn()} onStateChange={(next) => published.push({ dirty: next.dirty, pendingRestart: next.pendingRestart })} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  fireEvent.change(screen.getByLabelText("KV cache"), { target: { value: "q8_0" } });
  expect(published.at(-1)).toMatchObject({ dirty: true });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));

  await waitFor(() => expect(published.at(-1)).toMatchObject({ dirty: false, pendingRestart: true }));
});
