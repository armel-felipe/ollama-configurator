import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ResetControls } from "./ResetControls";

describe("ResetControls", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("requires confirmation before resetting every model", () => {
    const resetAll = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));
    render(<ResetControls onResetAll={resetAll} onResetModel={vi.fn()} selectedModel="qwen:latest" />);

    fireEvent.click(screen.getByRole("button", { name: /todos os modelos/i }));

    expect(window.confirm).toHaveBeenCalled();
    expect(resetAll).not.toHaveBeenCalled();
  });

  it("resets the selected model after confirmation", async () => {
    const resetModel = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(true));
    render(<ResetControls onResetAll={vi.fn()} onResetModel={resetModel} selectedModel="qwen:latest" />);

    fireEvent.click(screen.getByRole("button", { name: /modelo selecionado/i }));

    expect(resetModel).toHaveBeenCalledWith("qwen:latest");
  });
});
