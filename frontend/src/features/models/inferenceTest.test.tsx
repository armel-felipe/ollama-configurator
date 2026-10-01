import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { InferenceTestPanel } from "./InferenceTestPanel";

describe("InferenceTestPanel", () => {
  afterEach(() => cleanup());

  it("sends a prompt and renders requested thinking, received thinking, runtime, and final response", async () => {
    const run = vi.fn().mockResolvedValue({
      requested_profile: { think: false, num_ctx: 16384 },
      thinking: null,
      thinking_received: false,
      response: "Jânio Quadros",
      runtime: { loaded: true, context: 16384 },
    });
    render(<InferenceTestPanel modelId="gemma4:26b-mlx" runInference={run} />);

    fireEvent.change(screen.getByLabelText("Prompt de teste"), { target: { value: "Quem foi o 23º presidente do Brasil?" } });
    fireEvent.click(screen.getByRole("button", { name: "Executar teste" }));

    await waitFor(() => expect(run).toHaveBeenCalledWith("Quem foi o 23º presidente do Brasil?"));
    expect(screen.getByText("Thinking solicitado: false")).toBeInTheDocument();
    expect(screen.getByText("Thinking recebido: não")).toBeInTheDocument();
    expect(screen.getByText("Contexto efetivo: 16K")).toBeInTheDocument();
    expect(screen.getByText("Jânio Quadros")).toBeInTheDocument();
  });

  it("explains that an external ollama run session is independent", () => {
    render(<InferenceTestPanel modelId="qwen:latest" runInference={vi.fn()} />);
    expect(screen.getByText(/Este teste usa o perfil salvo/i)).toHaveTextContent(/sessão externa do/i);
  });
});
