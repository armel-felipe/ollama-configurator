import { getDiagnostics } from "./api/client";
import { DiagnosticsPage } from "./features/diagnostics/DiagnosticsPage";

export default function App() {
  return <DiagnosticsPage loadDiagnostics={getDiagnostics} />;
}
