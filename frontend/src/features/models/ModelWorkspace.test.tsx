import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ModelWorkspace } from "./ModelWorkspace";

describe("ModelWorkspace", () => {
  afterEach(() => cleanup());

  it("renders models as accessible selectable rows", () => {
    render(
      <ModelWorkspace
        models={[{ name: "qwen:latest" }, { name: "gemma:latest" }]}
        selectedModel="qwen:latest"
        onSelect={() => undefined}
      >
        <p>editor</p>
      </ModelWorkspace>,
    );

    expect(screen.getByRole("button", { name: "qwen:latest" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "gemma:latest" })).toHaveAttribute("aria-pressed", "false");
  });

  it("notifies the parent once when a model is selected", () => {
    const onSelect = vi.fn();
    render(<ModelWorkspace models={[{ name: "qwen:latest" }]} onSelect={onSelect}><p>editor</p></ModelWorkspace>);

    fireEvent.click(screen.getByRole("button", { name: "qwen:latest" }));
    expect(onSelect).toHaveBeenCalledOnce();
    expect(onSelect).toHaveBeenCalledWith("qwen:latest");
  });

  it("gives an actionable empty state", () => {
    render(<ModelWorkspace models={[]} onSelect={() => undefined}><p>editor</p></ModelWorkspace>);

    expect(screen.getByText(/nenhum modelo instalado/i)).toBeInTheDocument();
    expect(screen.getByText(/atualize a descoberta/i)).toBeInTheDocument();
  });

  it("keeps the main area explicit when no model is selected", () => {
    render(<ModelWorkspace models={[{ name: "qwen:latest" }]} onSelect={() => undefined} />);

    expect(screen.getByText(/selecione um modelo para configurar/i)).toBeInTheDocument();
  });
});
