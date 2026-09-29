import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AppShell } from "./AppShell";
import { ThemeProvider } from "./ThemeProvider";

describe("ThemeProvider", () => {
  afterEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
  });

  it("starts in light theme and toggles to dark with an accessible label", () => {
    render(
      <ThemeProvider>
        <AppShell selectedSection="models" onSectionChange={() => undefined}>
          <button type="button">conteúdo</button>
        </AppShell>
      </ThemeProvider>,
    );

    expect(document.documentElement.dataset.theme).toBe("light");
    fireEvent.click(screen.getByRole("button", { name: /tema escuro/i }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(screen.getByRole("button", { name: /tema claro/i })).toBeInTheDocument();
  });

  it("restores the persisted theme", () => {
    localStorage.setItem("ollama-configurator.theme", "dark");

    render(
      <ThemeProvider>
        <span>conteúdo</span>
      </ThemeProvider>,
    );

    expect(document.documentElement.dataset.theme).toBe("dark");
  });
});
