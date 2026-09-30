import type { ReactNode } from "react";
import { useTheme } from "./ThemeProvider";
import { OllamaLogo } from "./OllamaLogo";

export type WorkspaceSection = "models" | "server" | "diagnostics" | "connections";

type Props = {
  children: ReactNode;
  selectedSection: WorkspaceSection;
  onSectionChange: (section: WorkspaceSection) => void;
};

const sections: Array<{ id: WorkspaceSection; label: string; icon: string }> = [
  { id: "models", label: "Modelos", icon: "◇" },
  { id: "server", label: "Servidor", icon: "◌" },
  { id: "diagnostics", label: "Diagnóstico", icon: "⌁" },
  { id: "connections", label: "Conectar", icon: "↗" },
];

export function AppShell({ children, selectedSection, onSectionChange }: Props) {
  const { theme, toggleTheme } = useTheme();
  const targetTheme = theme === "light" ? "escuro" : "claro";

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#models" onClick={() => onSectionChange("models")}>
          <span className="brand-mark"><OllamaLogo /></span>
          <span>Ollama <strong>Configurator</strong></span>
        </a>
        <div className="topbar-actions">
          <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={`Alternar para tema ${targetTheme}`}>
            <span aria-hidden="true">{theme === "light" ? "☾" : "☀"}</span>
            Tema {targetTheme}
          </button>
        </div>
      </header>
      <div className="app-body">
        <nav className="workspace-nav" aria-label="Workspace">
          <div className="nav-caption">Workspace</div>
          {sections.map((section) => (
            <a
              key={section.id}
              href={`#${section.id}`}
              className={`nav-item${selectedSection === section.id ? " is-active" : ""}`}
              aria-current={selectedSection === section.id ? "page" : undefined}
              onClick={(event) => {
                event.preventDefault();
                onSectionChange(section.id);
              }}
            >
              <span className="nav-icon" aria-hidden="true">{section.icon}</span>
              {section.label}
            </a>
          ))}
          <div className="nav-footer"><span className="status-dot" aria-hidden="true" /> Gateway <span>11435</span></div>
        </nav>
        <main className="workspace-content">{children}</main>
      </div>
    </div>
  );
}
