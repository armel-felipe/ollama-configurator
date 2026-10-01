import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { RuntimeStatus } from "./RuntimeStatus";

describe("RuntimeStatus", () => {
  afterEach(() => cleanup());

  it("shows effective context and applied profile", () => {
    render(
      <RuntimeStatus
        runtime={{
          loaded: true,
          context: 65536,
          requested_context: 65536,
          context_matches: true,
          processor: "100% GPU",
          applied_options: { num_ctx: 65536, think: "high" },
        }}
      />,
    );

    expect(screen.getByText(/Contexto efetivo: 64K/)).toBeInTheDocument();
    expect(screen.getByText(/high/)).toBeInTheDocument();
  });

  it("exposes when Ollama loaded a different context", () => {
    render(
      <RuntimeStatus
        runtime={{
          loaded: true,
          context: 131072,
          requested_context: 65536,
          context_matches: false,
          applied_options: { num_ctx: 65536 },
        }}
      />,
    );

    expect(screen.getByText(/Contexto efetivo: 128K/)).toBeInTheDocument();
    expect(screen.getByText(/Contexto solicitado: 64K/)).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent(/não confirmou/i);
  });
});
