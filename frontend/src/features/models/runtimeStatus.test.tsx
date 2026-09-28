import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RuntimeStatus } from "./RuntimeStatus";

describe("RuntimeStatus", () => {
  it("shows effective context and applied profile", () => {
    render(
      <RuntimeStatus
        runtime={{
          loaded: true,
          context: 65536,
          processor: "100% GPU",
          applied_options: { num_ctx: 65536, think: "high" },
        }}
      />,
    );

    expect(screen.getByText(/Contexto: 64K/)).toBeInTheDocument();
    expect(screen.getByText(/high/)).toBeInTheDocument();
  });
});
