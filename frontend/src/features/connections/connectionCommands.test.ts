import { describe, expect, it } from "vitest";
import {
  buildConnectionCommand,
  connectionClients,
  type ConnectionClientId,
} from "./connectionCommands";

describe("connection command catalog", () => {
  it("contains every requested Ollama client", () => {
    expect(connectionClients.map((client) => client.id)).toEqual([
      "claude",
      "codex",
      "openclaw",
      "opencode",
      "hermes",
      "hermes-desktop",
      "droid",
      "pi",
      "cline",
      "copilot",
      "omp",
      "dsh",
      "pool",
      "qwen",
      "terminal",
    ] satisfies ConnectionClientId[]);
  });

  it("builds the launch command with the selected model and gateway host", () => {
    expect(buildConnectionCommand("opencode", "qwen3.8:27b-mlx", "posix", "http://127.0.0.1:11435"))
      .toBe("export OLLAMA_HOST=http://127.0.0.1:11435\nollama launch opencode --model qwen3.8:27b-mlx");
  });

  it("builds the Windows PowerShell command with the selected model", () => {
    expect(buildConnectionCommand("codex", "gemma4:26b-mlx", "powershell", "http://100.64.0.2:11435"))
      .toBe('$env:OLLAMA_HOST="http://100.64.0.2:11435"\nollama launch codex --model gemma4:26b-mlx');
  });

  it("keeps verbose as the final flag for the terminal card", () => {
    expect(buildConnectionCommand("terminal", "qwen3.8:27b-mlx", "posix", "http://127.0.0.1:11435"))
      .toBe("export OLLAMA_HOST=http://127.0.0.1:11435\nollama run qwen3.8:27b-mlx --verbose");
  });
});
