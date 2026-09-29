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

test("shows global settings before model selection and exposes restart-pending state", async () => {
  const update = vi.fn().mockResolvedValue({ ...state, pending_restart: true, settings: { OLLAMA_KV_CACHE_TYPE: "q8_0" } });
  const restart = vi.fn().mockResolvedValue({ success: true, detail: "ok", reapplied_models: [] });
  render(<ServerSettingsPage load={() => Promise.resolve(state)} update={update} restart={restart} reset={() => Promise.resolve(state)} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  expect(screen.getByLabelText("KV cache")).toHaveValue("f16");
  fireEvent.change(screen.getByLabelText("KV cache"), { target: { value: "q8_0" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar configurações" }));

  await waitFor(() => expect(update).toHaveBeenCalledWith({ OLLAMA_KV_CACHE_TYPE: "q8_0" }));
  expect(await screen.findByRole("status")).toHaveTextContent(/reinício pendente/i);
});

test("restart action reports model profile reapplication", async () => {
  const restart = vi.fn().mockResolvedValue({ success: true, detail: "ok", reapplied_models: ["gemma4:26b-mlx"] });
  render(<ServerSettingsPage load={() => Promise.resolve({ ...state, pending_restart: true })} update={vi.fn()} restart={restart} reset={() => Promise.resolve(state)} />);

  await screen.findByRole("heading", { name: "Configurações globais do Ollama" });
  fireEvent.click(screen.getByRole("button", { name: "Reiniciar Ollama" }));
  fireEvent.click(screen.getByRole("button", { name: "Confirmar reinício" }));

  await waitFor(() => expect(restart).toHaveBeenCalledTimes(1));
  expect(await screen.findByText(/perfis reaplicados/i)).toBeInTheDocument();
});
