import { useCallback, useEffect, useState } from "react";
import type { DiagnosticsSnapshot } from "../../api/client";
import {
  applyModelSettings,
  getModelSettings,
  getModelRuntime,
  resetAllModels,
  resetModel,
  saveModelSettings,
} from "../../api/client";
import { ErrorState, LoadingState } from "../shared/StatusState";
import { ModelsList } from "../models/ModelsList";
import { ModelSettingsPage } from "../models/ModelSettingsPage";
import { ResetControls } from "../settings/ResetControls";

type Props = { loadDiagnostics: () => Promise<DiagnosticsSnapshot> };

export function DiagnosticsPage({ loadDiagnostics }: Props) {
  const [data, setData] = useState<DiagnosticsSnapshot | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(() => {
    setError(null);
    void loadDiagnostics().then(setData).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Falha ao carregar diagnósticos");
    });
  }, [loadDiagnostics]);

  useEffect(() => { load(); }, [load]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return <LoadingState />;

  const memoryBytes = data.hardware.memoryBytes ?? data.hardware.memory_bytes;
  return (
    <main>
      <h1>Ollama Configurator</h1>
      <p>Ollama {data.ollama.available ? data.ollama.version : "indisponível"}</p>
      <section aria-labelledby="hardware-heading">
        <h2 id="hardware-heading">Hardware</h2>
        <p>{data.hardware.os} · {data.hardware.architecture}</p>
        {memoryBytes ? <p>{Math.round(memoryBytes / 1024 ** 3)} GB de memória</p> : null}
      </section>
      <ModelsList models={data.models} selectedModel={selectedModel} onSelect={setSelectedModel} />
      {selectedModel ? (
        <ModelSettingsPage
          modelId={selectedModel}
          loadSettings={() => getModelSettings(selectedModel)}
          saveSettings={(options) => saveModelSettings(selectedModel, options)}
          applySettings={() => applyModelSettings(selectedModel)}
          loadRuntime={() => getModelRuntime(selectedModel)}
        />
      ) : <p>Selecione um modelo para configurar.</p>}
      <ResetControls
        selectedModel={selectedModel}
        onResetAll={async () => { await resetAllModels(); load(); }}
        onResetModel={async (model) => { await resetModel(model); load(); }}
      />
    </main>
  );
}
