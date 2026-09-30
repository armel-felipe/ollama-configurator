import { describe, expect, it } from "vitest";

import { brandAssets, ollamaBrandAsset } from "./brandAssets";
import type { ConnectionClientId } from "../../features/connections/connectionCommands";

const clientIds: ConnectionClientId[] = [
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
];

describe("connection brand assets", () => {
  it("provides a local asset for every connection client", () => {
    expect(Object.keys(brandAssets).sort()).toEqual([...clientIds].sort());

    for (const id of clientIds) {
      expect(brandAssets[id].src).toMatch(/(?:\.(svg|png)(\?|$)|^data:image\/svg\+xml)/);
      expect(brandAssets[id].label).toBeTruthy();
      expect(["official", "licensed", "fallback"]).toContain(brandAssets[id].kind);
    }
  });

  it("provides the Ollama brand asset separately for the shell", () => {
    expect(ollamaBrandAsset.src).toMatch(/(?:\.svg(\?|$)|^data:image\/svg\+xml)/);
    expect(ollamaBrandAsset.label).toBe("Ollama");
  });
});
