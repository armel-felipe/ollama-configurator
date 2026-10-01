import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./features/diagnostics/DiagnosticsPage", () => ({
  DiagnosticsPage: () => (
    <>
      <h1>Configure seu runtime</h1>
      <div id="models-section" />
      <section id="server-section" />
      <section id="diagnostics-section" />
      <section id="connections-section" />
    </>
  ),
}));

describe("App", () => {
  afterEach(() => cleanup());

  it("renders the application shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /configure seu runtime/i })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: /workspace/i })).toBeInTheDocument();
    expect(screen.getByTestId("workspace-content-scroll")).toContainElement(
      screen.getByRole("heading", { name: /configure seu runtime/i }),
    );
  });

  it("updates the active section when a workspace area is selected", () => {
    render(<App />);

    expect(screen.getByRole("link", { name: "Modelos" })).toHaveAttribute("aria-current", "page");
    fireEvent.click(screen.getByRole("link", { name: "Servidor" }));

    expect(screen.getByRole("link", { name: "Servidor" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Modelos" })).not.toHaveAttribute("aria-current");
  });
});
