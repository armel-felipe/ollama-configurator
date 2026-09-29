import { useCallback, useEffect, useState } from "react";
import type { DiagnosticsSnapshot } from "../../api/client";
import {
  applyModelSettings,
  getModelSettings,
  getModelRuntime,
  getGatewayStatus,
  restartGateway,
  resetAllModels,
  resetModel,
  saveModelSettings,
  startGateway,
  stopGateway,
  getServerSettings,
  resetServerSettings,
  restartServer,
  saveServerSettings,
  restartApplication,
} from "../../api/client";
import { ErrorState, LoadingState } from "../shared/StatusState";
import { ModelWorkspace } from "../models/ModelWorkspace";
import { ModelSettingsPage } from "../models/ModelSettingsPage";
import { ResetControls } from "../settings/ResetControls";
import { GatewayControls } from "../gateway/GatewayControls";
import { ServerSettingsPage } from "../server/ServerSettingsPage";

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
    <div className="diagnostics-page">
      <div className="page-heading">
        <div>
          <div className="section-kicker">Modelos</div>
          <h1>Configure seu runtime</h1>
          <p>Escolha um modelo e ajuste o perfil que será aplicado ao Ollama.</p>
        </div>
        <div className="ollama-status"><span className="status-dot" aria-hidden="true" /> Ollama {data.ollama.available ? data.ollama.version : "indisponível"}</div>
      </div>
      <ServerSettingsPage load={getServerSettings} update={saveServerSettings} restart={restartServer} reset={resetServerSettings} restartApplication={restartApplication} />
      <GatewayControls
        getStatus={getGatewayStatus}
        start={startGateway}
        stop={stopGateway}
        restart={restartGateway}
      />
      <ModelWorkspace models={data.models} selectedModel={selectedModel} onSelect={setSelectedModel}>
        {selectedModel ? (
          <ModelSettingsPage
            modelId={selectedModel}
            loadSettings={() => getModelSettings(selectedModel)}
            saveSettings={(options) => saveModelSettings(selectedModel, options)}
            applySettings={() => applyModelSettings(selectedModel)}
            loadRuntime={() => getModelRuntime(selectedModel)}
          />
        ) : null}
      </ModelWorkspace>
      <section className="system-summary" aria-labelledby="system-heading">
        <div>
          <div className="section-kicker">Sistema</div>
          <h2 id="system-heading">Ambiente local</h2>
        </div>
        <p>{data.hardware.os} · {data.hardware.architecture}{memoryBytes ? ` · ${Math.round(memoryBytes / 1024 ** 3)} GB` : ""}</p>
      </section>
      <ResetControls
        selectedModel={selectedModel}
        onResetAll={async () => { await resetAllModels(); load(); }}
        onResetModel={async (model) => { await resetModel(model); load(); }}
      />
    </div>
  );
}
