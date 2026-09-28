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
