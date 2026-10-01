import type { ConnectionClientId } from "../../features/connections/connectionCommands";
import claude from "./claude.svg";
import cline from "./cline.svg";
import copilot from "./copilot.svg";
import codex from "./codex.svg";
import deepseekHarness from "./deepseek-harness.svg";
import droid from "./droid.svg";
import hermes from "./hermes.svg";
import ollama from "./ollama.svg";
import openclaw from "./openclaw.svg";
import opencode from "./opencode.svg";
import omp from "./omp.svg";
import pi from "./pi.svg";
import poolside from "./poolside.svg";
import qwen from "./qwen.svg";
import terminal from "./terminal.svg";

export type BrandAsset = {
  src: string;
  label: string;
  kind: "official" | "licensed" | "fallback";
};

export const brandAssets: Record<ConnectionClientId, BrandAsset> = {
  claude: { src: claude, label: "Claude Code", kind: "licensed" },
  codex: { src: codex, label: "Codex CLI", kind: "fallback" },
  openclaw: { src: openclaw, label: "OpenClaw", kind: "fallback" },
  opencode: { src: opencode, label: "OpenCode", kind: "licensed" },
  hermes: { src: hermes, label: "Hermes Agent", kind: "fallback" },
  "hermes-desktop": { src: hermes, label: "Hermes Desktop", kind: "fallback" },
  droid: { src: droid, label: "Droid", kind: "fallback" },
  pi: { src: pi, label: "Pi", kind: "licensed" },
  cline: { src: cline, label: "Cline", kind: "licensed" },
  copilot: { src: copilot, label: "Copilot CLI", kind: "licensed" },
  omp: { src: omp, label: "Oh My Pi", kind: "licensed" },
  dsh: { src: deepseekHarness, label: "DeepSeek Harness", kind: "licensed" },
  pool: { src: poolside, label: "Poolside", kind: "fallback" },
  qwen: { src: qwen, label: "Qwen Code", kind: "licensed" },
  terminal: { src: terminal, label: "Terminal", kind: "fallback" },
};

export const ollamaBrandAsset: BrandAsset = {
  src: ollama,
  label: "Ollama",
  kind: "official",
};
