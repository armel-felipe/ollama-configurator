import { describe, expect, it, vi } from "vitest";
import { deriveOperationalStatus, type OperationalAction, type OperationalInputs } from "./operationalStatus";

const action = (label: string): OperationalAction => ({ label, target: "server", run: vi.fn() });

const healthy: OperationalInputs = {
  ollamaAvailable: true,
  gateway: { state: "running", host: "127.0.0.1", port: 11435 },
  server: { available: true, pending_restart: false },
  serverDirty: false,
  runtime: null,
  actions: {},
};

describe("deriveOperationalStatus", () => {
  it("prioritizes unsaved server changes over an otherwise healthy gateway", () => {
    const status = deriveOperationalStatus({
      ...healthy,
      serverDirty: true,
      actions: { saveServer: action("Salvar configurações") },
    });

    expect(status.configuration.state).toBe("dirty");
    expect(status.primaryAction?.label).toBe("Salvar configurações");
  });

  it("reports pending application after settings are saved", () => {
    const status = deriveOperationalStatus({
      ...healthy,
      server: { available: true, pending_restart: true },
      actions: { applyServer: action("Aplicar no Ollama") },
    });

    expect(status.configuration.state).toBe("pending");
    expect(status.primaryAction?.label).toBe("Aplicar no Ollama");
  });

  it("reports an external gateway without offering a destructive action", () => {
    const status = deriveOperationalStatus({
      ...healthy,
      gateway: { state: "external", host: "127.0.0.1", port: 11435 },
      actions: { startGateway: action("Iniciar gateway") },
    });

    expect(status.gateway.state).toBe("external");
    expect(status.gateway.detail).toMatch(/outro processo/i);
    expect(status.primaryAction).toBeNull();
  });

  it("reports a pending gateway bind separately from an active process", () => {
    const status = deriveOperationalStatus({
      ...healthy,
      gatewayPending: true,
    });

    expect(status.gateway.state).toBe("pending");
    expect(status.gateway.label).toMatch(/bind pendente/i);
    expect(status.gateway.detail).toMatch(/endereço/i);
  });

  it("prioritizes a divergent runtime after configuration is applied", () => {
    const status = deriveOperationalStatus({
      ...healthy,
      runtime: { loaded: true, context_matches: false, applied_options: {} },
      actions: { applyModel: { ...action("Reaplicar perfil"), target: "model" } },
    });

    expect(status.runtime.state).toBe("divergent");
    expect(status.primaryAction?.label).toBe("Reaplicar perfil");
  });
});
