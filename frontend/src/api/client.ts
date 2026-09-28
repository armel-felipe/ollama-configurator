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
  const response = await fetch("/api/diagnostics");
  if (!response.ok) throw new Error("Não foi possível carregar os diagnósticos");
  return response.json() as Promise<DiagnosticsSnapshot>;
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

export async function resetAllModels(): Promise<void> {
  const response = await fetch("/api/reset/models", { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível restaurar os modelos");
}

export async function resetModel(modelId: string): Promise<void> {
  const response = await fetch(`/api/models/${encodeURIComponent(modelId)}/reset`, { method: "POST" });
  if (!response.ok) throw new Error("Não foi possível restaurar o modelo");
}
