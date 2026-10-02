export type ShellKind = "posix" | "powershell";

export function defaultShellForUserAgent(userAgent: string): ShellKind {
  return /Windows/i.test(userAgent) ? "powershell" : "posix";
}

export function gatewayUrlForIp(ip: string, port: number): string {
  const host = ip.includes(":") ? `[${ip}]` : ip;
  return `http://${host}:${port}`;
}

export type ConnectionClientId =
  | "claude"
  | "codex"
  | "openclaw"
  | "opencode"
  | "hermes"
  | "hermes-desktop"
  | "droid"
  | "pi"
  | "cline"
  | "copilot"
  | "omp"
  | "dsh"
  | "pool"
  | "qwen"
  | "terminal";

export type ConnectionClient = {
  id: ConnectionClientId;
  label: string;
  description: string;
};

export const connectionClients: ConnectionClient[] = [
  { id: "claude", label: "Claude Code", description: "Assistente de código da Anthropic" },
  { id: "codex", label: "Codex CLI", description: "Assistente de código no terminal" },
  { id: "openclaw", label: "OpenClaw", description: "Agente de desenvolvimento local" },
  { id: "opencode", label: "OpenCode", description: "Agente de código open source" },
  { id: "hermes", label: "Hermes Agent", description: "Agente local para tarefas técnicas" },
  { id: "hermes-desktop", label: "Hermes Desktop", description: "Experiência desktop do Hermes" },
  { id: "droid", label: "Droid", description: "Agente de engenharia no terminal" },
  { id: "pi", label: "Pi", description: "Assistente de programação local" },
  { id: "cline", label: "Cline", description: "Agente de código para seu editor" },
  { id: "copilot", label: "Copilot CLI", description: "Copilot direto no terminal" },
  { id: "omp", label: "Oh My Pi", description: "Ambiente Pi para desenvolvimento" },
  { id: "dsh", label: "DeepSeek Harness", description: "Harness para agentes DeepSeek" },
  { id: "pool", label: "Poolside", description: "Ferramentas de código assistido" },
  { id: "qwen", label: "Qwen Code", description: "Ferramenta de código da Qwen" },
  { id: "terminal", label: "Terminal", description: "Executar um modelo no Ollama" },
];

function ollamaCommand(clientId: ConnectionClientId, model: string): string {
  if (clientId === "terminal") return `ollama run ${model} --verbose`;
  return `ollama launch ${clientId} --model ${model}`;
}

function normalizeHost(host: string): string {
  const markdownLink = host.trim().match(/^\[[^\]]+\]\(([^)]+)\)$/);
  return markdownLink?.[1] ?? host.trim();
}

export function buildConnectionCommand(
  clientId: ConnectionClientId,
  model: string,
  shell: ShellKind,
  host: string,
): string {
  const normalizedHost = normalizeHost(host);
  const environment = shell === "powershell"
    ? `$env:OLLAMA_HOST="${normalizedHost}"`
    : `export OLLAMA_HOST=${normalizedHost}`;
  return `${environment}\n${ollamaCommand(clientId, model)}`;
}
