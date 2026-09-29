import type { GatewayStatus, RuntimeStatus, ServerSettingsState } from "../../api/client";

export type OperationalIndicator =
  | "active"
  | "unavailable"
  | "stopped"
  | "starting"
  | "external"
  | "error"
  | "saved"
  | "dirty"
  | "pending"
  | "applied"
  | "unverified"
  | "divergent";

export type OperationalAction = {
  label: string;
  target: "application" | "gateway" | "server" | "model" | "diagnostics";
  run: () => void | Promise<void>;
};

export type OperationalStatus = {
  application: { state: "active" | "unavailable"; label: string; detail: string };
  gateway: { state: OperationalIndicator; label: string; detail: string };
  configuration: { state: "loading" | "saved" | "dirty" | "pending"; label: string; detail: string };
  runtime: { state: "applied" | "unverified" | "divergent"; label: string; detail: string };
  primaryAction: OperationalAction | null;
};

export type OperationalInputs = {
  ollamaAvailable: boolean;
  gateway: GatewayStatus | null;
  gatewayError?: string | null;
  server: Pick<ServerSettingsState, "available" | "pending_restart"> | null;
  serverDirty: boolean;
  serverError?: string | null;
  runtime: RuntimeStatus | null;
  runtimeError?: string | null;
  actions: {
    startGateway?: OperationalAction;
    retryGateway?: OperationalAction;
    saveServer?: OperationalAction;
    applyServer?: OperationalAction;
    retryServer?: OperationalAction;
    applyModel?: OperationalAction;
    retryRuntime?: OperationalAction;
  };
};

function gatewayStatus(input: OperationalInputs): OperationalStatus["gateway"] {
  if (input.gatewayError) return { state: "error", label: "Gateway com erro", detail: input.gatewayError };
  if (!input.gateway) return { state: "starting", label: "Gateway consultando", detail: "Consultando a porta 11435." };
  if (input.gateway.state === "running") return { state: "active", label: "Gateway ativo", detail: `Respondendo em ${input.gateway.host}:${input.gateway.port}.` };
  if (input.gateway.state === "external") return { state: "external", label: "Gateway externo", detail: "Outro processo está usando a porta; a aplicação não o controla." };
  if (input.gateway.state === "starting") return { state: "starting", label: "Gateway iniciando", detail: "Aguardando o gateway responder." };
  if (input.gateway.state === "error") return { state: "error", label: "Gateway com erro", detail: input.gateway.detail ?? "Não foi possível iniciar o gateway." };
  return { state: "stopped", label: "Gateway parado", detail: "A porta 11435 não está respondendo." };
}

function configurationStatus(input: OperationalInputs): OperationalStatus["configuration"] {
  if (!input.server) return { state: "loading", label: "Configuração consultando", detail: "Carregando as configurações globais." };
  if (input.serverError) return { state: "pending", label: "Configuração indisponível", detail: input.serverError };
  if (input.serverDirty) return { state: "dirty", label: "Alterações não salvas", detail: "Há valores editados apenas nesta tela." };
  if (input.server.pending_restart) return { state: "pending", label: "Aplicação pendente", detail: "As configurações foram salvas, mas ainda não foram aplicadas ao Ollama." };
  return { state: "saved", label: "Configuração salva", detail: "Não há alterações globais aguardando aplicação." };
}

function runtimeStatus(input: OperationalInputs): OperationalStatus["runtime"] {
  if (input.runtimeError) return { state: "unverified", label: "Runtime não confirmado", detail: input.runtimeError };
  if (!input.runtime) return { state: "unverified", label: "Runtime não verificado", detail: "Aplique um perfil para confirmar o valor efetivo." };
  if (input.runtime.context_matches === false) return { state: "divergent", label: "Runtime divergente", detail: "O valor efetivo não corresponde ao valor solicitado." };
  return { state: "applied", label: "Runtime confirmado", detail: "O valor efetivo foi observado no modelo." };
}

export function deriveOperationalStatus(input: OperationalInputs): OperationalStatus {
  const gateway = gatewayStatus(input);
  const configuration = configurationStatus(input);
  const runtime = runtimeStatus(input);
  const application = input.ollamaAvailable
    ? { state: "active" as const, label: "Aplicação ativa", detail: "O backend local respondeu." }
    : { state: "unavailable" as const, label: "Aplicação indisponível", detail: "O backend local não respondeu." };

  let primaryAction: OperationalAction | null = null;
  if (!input.ollamaAvailable) primaryAction = input.actions.retryServer ?? null;
  else if (input.gatewayError) primaryAction = input.actions.retryGateway ?? null;
  else if (input.serverError) primaryAction = input.actions.retryServer ?? null;
  else if (configuration.state === "dirty") primaryAction = input.actions.saveServer ?? null;
  else if (configuration.state === "pending") primaryAction = input.actions.applyServer ?? null;
  else if (gateway.state === "stopped") primaryAction = input.actions.startGateway ?? null;
  else if (runtime.state === "divergent") primaryAction = input.actions.applyModel ?? null;
  else if (runtime.state === "unverified") primaryAction = input.actions.retryRuntime ?? null;

  return { application, gateway, configuration, runtime, primaryAction };
}
