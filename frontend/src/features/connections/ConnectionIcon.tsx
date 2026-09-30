import type { ConnectionClientId } from "./connectionCommands";

type Props = { id: ConnectionClientId; className?: string };

export function ConnectionIcon({ id, className = "" }: Props) {
  const common = { className: `connection-icon ${className}`, viewBox: "0 0 48 48", fill: "none", "aria-hidden": true } as const;
  switch (id) {
    case "terminal":
      return <svg {...common}><rect x="7" y="9" width="34" height="30" rx="6" stroke="currentColor" strokeWidth="3" /><path d="m15 19 7 5-7 5M26 30h7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "claude":
      return <svg {...common}><path d="M13 32c3-11 7-17 11-17s8 6 11 17M17 25h14M14 32h20" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
    case "codex":
      return <svg {...common}><path d="m24 8 5 5 7-1 1 7 5 5-5 5-1 7-7-1-5 5-5-5-7 1-1-7-5-5 5-5 1-7 7 1 5-5Z" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" /><path d="M18 30V18h7a4 4 0 0 1 0 8h-7m7-8 5 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" /></svg>;
    case "openclaw":
      return <svg {...common}><path d="M11 29c-5-3-4-11 2-13 2-7 12-9 17-4 7-1 10 8 5 12-1 7-9 10-15 6l-6 4 1-6Z" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" /><path d="m12 21-5-3m7 1-2-6m18 5 6-4m-7 7 5 2" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" /></svg>;
    case "opencode":
      return <svg {...common}><path d="M24 8 39 16v16L24 40 9 32V16L24 8Z" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" /><path d="m18 24 4 4 9-10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "hermes":
    case "hermes-desktop":
      return <svg {...common}><path d="M13 36V17l11-6 11 6v19M13 25h22M20 18v18m8-18v18" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" /><path d="M17 39h14" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
    case "droid":
    case "cline":
      return <svg {...common}><rect x="10" y="16" width="28" height="23" rx="8" stroke="currentColor" strokeWidth="3" /><path d="M17 16 14 11m17 5 3-5M24 9v4M18 26h.01M30 26h.01M19 33h10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
    case "pi":
    case "omp":
      return <svg {...common}><circle cx="24" cy="24" r="15" stroke="currentColor" strokeWidth="3" /><path d="M18 17h11a5 5 0 0 1 0 10H18m0-10v16" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
    case "copilot":
      return <svg {...common}><path d="M12 28c-4-10 4-18 12-18s16 8 12 18c-2 6-7 10-12 10s-10-4-12-10Z" stroke="currentColor" strokeWidth="3" /><path d="M17 26c2-4 4-4 7 0 3-4 5-4 7 0M18 19h.01M30 19h.01" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
    case "dsh":
      return <svg {...common}><path d="M12 16c7-8 17-8 24 0M10 25c8-6 20-6 28 0M15 34c6-3 12-3 18 0" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /><circle cx="24" cy="24" r="3" fill="currentColor" /></svg>;
    case "pool":
      return <svg {...common}><circle cx="24" cy="24" r="15" stroke="currentColor" strokeWidth="3" /><path d="M17 29c5-12 9-12 14-10-5 1-8 4-9 10m-5-7c3 1 6 3 8 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "qwen":
      return <svg {...common}><path d="M10 27c0-10 6-17 15-17 8 0 13 5 13 13 0 10-7 16-16 16-7 0-12-4-12-10Z" stroke="currentColor" strokeWidth="3" /><path d="M18 23c2-3 5-4 8-2m-8 8c4 2 8 1 11-2" stroke="currentColor" strokeWidth="3" strokeLinecap="round" /></svg>;
  }
}
