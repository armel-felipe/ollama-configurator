import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppShell } from "./AppShell";
import { ThemeProvider } from "./ThemeProvider";

describe("AppShell", () => {
  it("renders accessible workspace navigation and marks the active section", () => {
    render(
      <ThemeProvider>
        <AppShell selectedSection="models" onSectionChange={() => undefined}>
          <h1>Área de trabalho</h1>
        </AppShell>
      </ThemeProvider>,
    );

    expect(screen.getByRole("navigation", { name: /workspace/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /modelos/i })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: /servidor/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /diagnóstico/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /área de trabalho/i })).toBeInTheDocument();
    expect(screen.queryByText(/ollama conectado/i)).not.toBeInTheDocument();
  });
});
