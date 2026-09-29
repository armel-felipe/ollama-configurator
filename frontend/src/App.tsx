import { getDiagnostics } from "./api/client";
import { DiagnosticsPage } from "./features/diagnostics/DiagnosticsPage";
import { AppShell } from "./features/shell/AppShell";
import { ThemeProvider } from "./features/shell/ThemeProvider";

export default function App() {
  return (
    <ThemeProvider>
      <AppShell selectedSection="models" onSectionChange={() => undefined}>
        <DiagnosticsPage loadDiagnostics={getDiagnostics} />
      </AppShell>
    </ThemeProvider>
  );
}
