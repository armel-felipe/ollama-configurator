import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { OperationalStatus } from "./operationalStatus";
import { OperationalStatusSummary } from "./OperationalStatusSummary";

const pendingStatus: OperationalStatus = {
  application: { state: "active", label: "Aplicação ativa", detail: "O backend local respondeu." },
  gateway: { state: "active", label: "Gateway ativo", detail: "Respondendo em 127.0.0.1:11435." },
  configuration: { state: "pending", label: "Aplicação pendente", detail: "As configurações foram salvas, mas ainda não foram aplicadas ao Ollama." },
  runtime: { state: "unverified", label: "Runtime não verificado", detail: "Aplique um perfil para confirmar o valor efetivo." },
  primaryAction: { label: "Aplicar no Ollama", target: "server", run: vi.fn() },
};

describe("OperationalStatusSummary", () => {
  afterEach(() => document.body.replaceChildren());

  it("renders four readable status indicators and one contextual action", () => {
    render(<OperationalStatusSummary status={pendingStatus} />);

    expect(screen.getByRole("region", { name: /estado operacional/i })).toBeInTheDocument();
    expect(screen.getByText("Aplicação ativa")).toBeInTheDocument();
    expect(screen.getByText("Gateway ativo")).toBeInTheDocument();
    expect(screen.getByText("Aplicação pendente")).toBeInTheDocument();
    expect(screen.getByText("Runtime não verificado")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Aplicar no Ollama" })).toBeInTheDocument();
  });

  it("does not render an action when all states are settled", () => {
    render(
      <OperationalStatusSummary
        status={{
          ...pendingStatus,
          configuration: { state: "saved", label: "Configuração salva", detail: "Não há alterações globais aguardando aplicação." },
          runtime: { state: "applied", label: "Runtime confirmado", detail: "O valor efetivo foi observado no modelo." },
          primaryAction: null,
        }}
      />,
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
