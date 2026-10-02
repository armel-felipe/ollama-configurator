import { describe, expect, it } from "vitest";
import {
  buildConnectionCommand,
  connectionClients,
  defaultShellForUserAgent,
  gatewayUrlForIp,
  type ConnectionClientId,
} from "./connectionCommands";

describe("gatewayUrlForIp", () => {
  it("formats IPv4 without brackets", () => {
    expect(gatewayUrlForIp("100.87.71.48", 11435)).toBe("http://100.87.71.48:11435");
  });

  it("brackets IPv6 for an HTTP URL", () => {
    expect(gatewayUrlForIp("fd7a:115c:a1e0::1", 11435)).toBe("http://[fd7a:115c:a1e0::1]:11435");
  });
});

describe("connection command catalog", () => {
  it.each([
    ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "powershell"],
    ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "posix"],
    ["Mozilla/5.0 (X11; Linux x86_64)", "posix"],
    ["Unknown Device", "posix"],
  ])("selects the default shell for %s", (userAgent, expected) => {
    expect(defaultShellForUserAgent(userAgent)).toBe(expected);
  });
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

  it("normalizes a Markdown-formatted host before copying", () => {
    expect(buildConnectionCommand(
      "terminal",
      "gemma4:26b-mlx",
      "posix",
      "[http://127.0.0.1:11435](http://127.0.0.1:11435)",
    )).toBe("export OLLAMA_HOST=http://127.0.0.1:11435\nollama run gemma4:26b-mlx --verbose");
  });
});
