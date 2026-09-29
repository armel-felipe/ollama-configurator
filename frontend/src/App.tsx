import { useState } from "react";
import { getDiagnostics } from "./api/client";
import { DiagnosticsPage } from "./features/diagnostics/DiagnosticsPage";
import { AppShell, type WorkspaceSection } from "./features/shell/AppShell";
import { ThemeProvider } from "./features/shell/ThemeProvider";

export default function App() {
  const [selectedSection, setSelectedSection] = useState<WorkspaceSection>("models");

  const selectSection = (section: WorkspaceSection) => {
    setSelectedSection(section);
    window.requestAnimationFrame(() => {
      document.getElementById(`${section}-section`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  };

  return (
    <ThemeProvider>
      <AppShell selectedSection={selectedSection} onSectionChange={selectSection}>
        <DiagnosticsPage loadDiagnostics={getDiagnostics} />
      </AppShell>
    </ThemeProvider>
  );
}
