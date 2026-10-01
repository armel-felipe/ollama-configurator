export type DiagnosticsSnapshot = {
  ollama: { available: boolean; version?: string; error?: string };
  hardware: {
    os: string;
    architecture: string;
    memory_bytes?: number;
    memoryBytes?: number;
    gpu_vendor?: string;
    backends?: string[];
  };
  models: Array<{ name: string; size?: number }>;
};

export async function getDiagnostics(): Promise<DiagnosticsSnapshot> {
  let response: Response;
  try {
    response = await fetch("/api/diagnostics");
  } catch (error) {
    throw new Error(
      "O backend local não está respondendo em 127.0.0.1:8787. Inicie a aplicação pelo launcher de desenvolvimento e tente novamente.",
      { cause: error },
    );
  }
  if (!response.ok) throw new Error("Não foi possível carregar os diagnósticos");
  return response.json() as Promise<DiagnosticsSnapshot>;
}

export async function restartApplication(): Promise<void> {
  const response = await fetch("/api/application/restart", { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível reiniciar a aplicação");
}

export async function getModelSettings(modelId: string): Promise<{
  options: Record<string, number | string | boolean>;
  thinking?: { values: Array<boolean | string>; default?: boolean | string | null } | null;
  defaults?: Record<string, string>;
}> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/settings`);
  if (!response.ok) throw new Error("Não foi possível carregar as configurações");
  return response.json() as Promise<{ options: Record<string, number | string> }>;
}

export type RuntimeStatus = {
  model?: string;
  loaded: boolean;
  context?: number | null;
  requested_context?: number | null;
  context_matches?: boolean | null;
  processor?: string | null;
  until?: string | null;
  applied_options: Record<string, number | string | boolean>;
  observed_at?: string;
};

export async function getModelRuntime(modelId: string): Promise<RuntimeStatus> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/runtime`);
  if (!response.ok) throw new Error("Não foi possível consultar o runtime");
  return response.json() as Promise<RuntimeStatus>;
}

export async function saveModelSettings(
  modelId: string,
  options: Record<string, number | string | boolean>,
): Promise<unknown> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  });
  if (!response.ok) throw new Error("Não foi possível salvar as configurações");
  return response.json();
}

export async function applyModelSettings(modelId: string): Promise<unknown> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/apply`, { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível aplicar as configurações");
  return response.json();
}

export type InferenceTestResult = {
  model: string;
  requested_profile: Record<string, number | string | boolean>;
  thinking?: string | null;
  thinking_received: boolean;
  response: string;
  runtime: RuntimeStatus;
};

export async function runInferenceTest(modelId: string, prompt: string): Promise<InferenceTestResult> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/inference-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível executar o teste de inferência");
  }
  return response.json() as Promise<InferenceTestResult>;
}

export async function resetAllModels(): Promise<void> {
  const response = await fetch("/api/reset/models", { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível restaurar os modelos");
}

export async function resetModel(modelId: string): Promise<void> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/reset`, { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível restaurar o modelo");
}

export type GatewayStatus = {
  state: "stopped" | "starting" | "running" | "external" | "error";
  host: string;
  port: number;
  pid?: number | null;
  process?: string | null;
  detail?: string | null;
};

export type GatewaySettings = {
  host: string;
  effective_host: string;
  port: number;
  pending_restart: boolean;
  options: string[];
  warning?: string | null;
};

export type GatewayApplyResult = {
  status: GatewayStatus;
  settings: GatewaySettings;
};

async function gatewayAction(path: string): Promise<GatewayStatus> {
  const response = await fetch(`/api/gateway/${path}`, { method: path === "status" ? "GET" : "POST" });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível controlar o servidor");
  }
  return response.json() as Promise<GatewayStatus>;
}

export function getGatewayStatus(): Promise<GatewayStatus> {
  return gatewayAction("status");
}

export function startGateway(): Promise<GatewayStatus> {
  return gatewayAction("start");
}

export function stopGateway(): Promise<GatewayStatus> {
  return gatewayAction("stop");
}

export function restartGateway(): Promise<GatewayStatus> {
  return gatewayAction("restart");
}

export function releaseExternalGateway(): Promise<GatewayStatus> {
  return gatewayAction("release-external");
}

export async function getGatewaySettings(): Promise<GatewaySettings> {
  const response = await fetch("/api/gateway/settings");
  if (!response.ok) throw new Error("Não foi possível carregar o acesso do gateway");
  return response.json() as Promise<GatewaySettings>;
}

export async function saveGatewaySettings(host: string): Promise<GatewaySettings> {
  const response = await fetch("/api/gateway/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ host }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível salvar o acesso do gateway");
  }
  return response.json() as Promise<GatewaySettings>;
}

export async function applyGatewaySettings(): Promise<GatewayApplyResult> {
  const response = await fetch("/api/gateway/apply", { method: "POST" });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível aplicar o acesso do gateway");
  }
  return response.json() as Promise<GatewayApplyResult>;
}

export type ServerSettingCapability = {
  label: string;
  description: string;
  type: "select" | "boolean" | "number" | "text";
  options?: string[];
  presets?: Array<{ label: string; value: number }>;
  default: string | number | boolean;
  min?: number;
};

export type ServerSettingsState = {
  settings: Record<string, string | number | boolean>;
  effective: Record<string, string | number | boolean>;
  pending_restart: boolean;
  available: boolean;
  capabilities: Record<string, ServerSettingCapability>;
};

export type ServerRestartResult = { success: boolean; detail: string; reapplied_models: string[] };

export async function getServerSettings(): Promise<ServerSettingsState> {
  const response = await fetch("/api/server/settings");
  if (!response.ok) throw new Error("Não foi possível carregar as configurações globais");
  return response.json() as Promise<ServerSettingsState>;
}

export async function saveServerSettings(
  patch: Record<string, string | number | boolean | "default">,
): Promise<ServerSettingsState> {
  const response = await fetch("/api/server/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível salvar as configurações globais");
  }
  return response.json() as Promise<ServerSettingsState>;
}

export async function resetServerSettings(): Promise<ServerSettingsState> {
  const response = await fetch("/api/server/settings/reset", { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível restaurar as configurações globais");
  return response.json() as Promise<ServerSettingsState>;
}

export async function restartServer(): Promise<ServerRestartResult> {
  const response = await fetch("/api/server/restart", { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível reiniciar o Ollama");
  return response.json() as Promise<ServerRestartResult>;
}
