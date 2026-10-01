import { useCallback, useEffect, useState } from "react";
import type { DiagnosticsSnapshot } from "../../api/client";
import {
  applyModelSettings,
  getModelSettings,
  getModelRuntime,
  getGatewayStatus,
  getGatewaySettings,
  restartGateway,
  releaseExternalGateway,
  resetAllModels,
  resetModel,
  saveModelSettings,
  startGateway,
  stopGateway,
  saveGatewaySettings,
  applyGatewaySettings,
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
import { OperationalStatusSummary } from "../status/OperationalStatusSummary";
import { LiveLogsPanel } from "../logs/LiveLogsPanel";
import { ConnectionsPage } from "../connections/ConnectionsPage";
import { deriveOperationalStatus, type OperationalAction } from "../status/operationalStatus";

type Props = { loadDiagnostics: () => Promise<DiagnosticsSnapshot> };

export function DiagnosticsPage({ loadDiagnostics }: Props) {
  const [data, setData] = useState<DiagnosticsSnapshot | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [serverView, setServerView] = useState<{ loaded: boolean; available: boolean; pendingRestart: boolean; dirty: boolean; error: string | null }>({ loaded: false, available: false, pendingRestart: false, dirty: false, error: null });
  const [gatewayView, setGatewayView] = useState<{ status: Awaited<ReturnType<typeof getGatewayStatus>> | null; error: string | null; pending: boolean }>({ status: null, error: null, pending: false });
  const [modelView, setModelView] = useState<{ selected: boolean; dirty: boolean; runtime: Awaited<ReturnType<typeof getModelRuntime>> | null; error: string | null }>({ selected: false, dirty: false, runtime: null, error: null });
  const handleGatewayState = useCallback((status: Awaited<ReturnType<typeof getGatewayStatus>>, gatewayError: string | null, pending = false) => setGatewayView({ status, error: gatewayError, pending }), []);
  const handleModelState = useCallback((next: { selected: boolean; dirty: boolean; runtime: Awaited<ReturnType<typeof getModelRuntime>> | null; error: string | null }) => setModelView(next), []);
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
  const scrollAction = (label: string, target: OperationalAction["target"], id: string): OperationalAction => ({
    label,
    target,
    run: () => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" }),
  });
  const operationalStatus = deriveOperationalStatus({
    ollamaAvailable: data.ollama.available,
    gateway: gatewayView.status,
    gatewayPending: gatewayView.pending,
    gatewayError: gatewayView.error,
    server: serverView.loaded ? { available: serverView.available, pending_restart: serverView.pendingRestart } : null,
    serverDirty: serverView.dirty,
    serverError: serverView.error,
    runtime: modelView.runtime,
    runtimeError: modelView.error,
    actions: {
      startGateway: scrollAction("Ver gateway", "gateway", "gateway-section"),
      retryGateway: scrollAction("Revisar gateway", "gateway", "gateway-section"),
      saveServer: scrollAction("Salvar configurações", "server", "server-section"),
      applyServer: scrollAction("Aplicar no Ollama", "server", "server-section"),
      retryServer: scrollAction("Recarregar configurações", "server", "server-section"),
      applyModel: scrollAction("Reaplicar perfil", "model", "model-profile-section"),
    },
  });
  return (
    <div className="diagnostics-page">
      <div className="page-heading" id="models-section">
        <div>
          <div className="section-kicker">Modelos</div>
          <h1>Configure seu runtime</h1>
          <p>Escolha um modelo e ajuste o perfil que será aplicado ao Ollama.</p>
        </div>
        <div className="ollama-status"><span className="status-dot" aria-hidden="true" /> Ollama {data.ollama.available ? data.ollama.version : "indisponível"}</div>
      </div>
      <OperationalStatusSummary status={operationalStatus} />
      <LiveLogsPanel />
      <ServerSettingsPage load={getServerSettings} update={saveServerSettings} restart={restartServer} reset={resetServerSettings} restartApplication={restartApplication} onStateChange={setServerView} />
      <GatewayControls
        getStatus={getGatewayStatus}
        start={startGateway}
        stop={stopGateway}
        restart={restartGateway}
        releaseExternal={releaseExternalGateway}
        getSettings={getGatewaySettings}
        updateSettings={saveGatewaySettings}
        applySettings={applyGatewaySettings}
        onStateChange={handleGatewayState}
      />
      <ModelWorkspace models={data.models} selectedModel={selectedModel} onSelect={setSelectedModel}>
        {selectedModel ? (
          <ModelSettingsPage
            modelId={selectedModel}
            loadSettings={() => getModelSettings(selectedModel)}
            saveSettings={(options) => saveModelSettings(selectedModel, options)}
            applySettings={() => applyModelSettings(selectedModel)}
            loadRuntime={() => getModelRuntime(selectedModel)}
            onStateChange={handleModelState}
          />
        ) : null}
      </ModelWorkspace>
      <ConnectionsPage
        models={data.models}
        selectedModel={selectedModel}
        gateway={gatewayView.status}
        onSelectModel={setSelectedModel}
      />
      <section className="system-summary" id="diagnostics-section" aria-labelledby="system-heading">
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
