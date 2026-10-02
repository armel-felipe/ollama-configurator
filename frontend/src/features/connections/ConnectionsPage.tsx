import { useEffect, useRef, useState } from "react";
import type { GatewaySettings, GatewayStatus } from "../../api/client";
import {
  buildConnectionCommand,
  connectionClients,
  defaultShellForUserAgent,
  gatewayUrlForIp,
  type ConnectionClientId,
  type ShellKind,
} from "./connectionCommands";
import { ConnectionIcon } from "./ConnectionIcon";

type Model = { name: string; size?: number };

type Props = {
  models: Model[];
  selectedModel?: string;
  gateway: GatewayStatus | null;
  onSelectModel: (model: string) => void;
  loadGatewaySettings: () => Promise<GatewaySettings>;
  saveTailscaleIp: (ip: string) => Promise<GatewaySettings>;
};

const fallbackHost = "http://127.0.0.1:11435";

export function ConnectionsPage({ models, selectedModel, gateway, onSelectModel, loadGatewaySettings, saveTailscaleIp }: Props) {
  const [selectedClient, setSelectedClient] = useState<ConnectionClientId>("terminal");
  const [shell, setShell] = useState<ShellKind>(() => defaultShellForUserAgent(navigator.userAgent));
  const [copiedClient, setCopiedClient] = useState<ConnectionClientId | null>(null);
  const [draftTailscaleIp, setDraftTailscaleIp] = useState("");
  const [savedTailscaleIp, setSavedTailscaleIp] = useState<string | null>(null);
  const [tailscaleStatus, setTailscaleStatus] = useState<"idle" | "saving" | "success">("idle");
  const [tailscaleError, setTailscaleError] = useState<string | null>(null);
  const tailscaleInputRef = useRef<HTMLInputElement>(null);
  const settingsVersionRef = useRef(0);
  const networkBind = gateway?.host === "0.0.0.0";
  const host = gateway
    ? networkBind && savedTailscaleIp
      ? gatewayUrlForIp(savedTailscaleIp, gateway.port)
      : networkBind
        ? null
        : `http://${gateway.host}:${gateway.port}`
    : fallbackHost;
  const client = connectionClients.find((item) => item.id === selectedClient) ?? connectionClients[0];
  const gatewayRunning = gateway?.state === "running";

  useEffect(() => {
    let active = true;
    const settingsVersion = ++settingsVersionRef.current;
    void loadGatewaySettings().then((settings) => {
      if (!active || settingsVersion !== settingsVersionRef.current) return;
      setSavedTailscaleIp(settings.tailscale_ip ?? null);
      setDraftTailscaleIp(settings.tailscale_ip ?? "");
    }).catch((reason: unknown) => {
      if (!active || settingsVersion !== settingsVersionRef.current) return;
      setTailscaleError(reason instanceof Error ? reason.message : "Não foi possível carregar o IP Tailscale");
    });
    return () => { active = false; };
  }, [loadGatewaySettings]);

  async function saveIp() {
    settingsVersionRef.current += 1;
    setTailscaleStatus("saving");
    setTailscaleError(null);
    try {
      const settings = await saveTailscaleIp(draftTailscaleIp.trim());
      setSavedTailscaleIp(settings.tailscale_ip ?? null);
      setDraftTailscaleIp(settings.tailscale_ip ?? "");
      setTailscaleStatus("success");
    } catch (reason: unknown) {
      setTailscaleStatus("idle");
      setTailscaleError(reason instanceof Error ? reason.message : "Não foi possível salvar o IP Tailscale");
    }
  }

  async function copyCommand(clientId: ConnectionClientId) {
    if (!selectedModel) return;
    if (host === null) {
      setTailscaleError("Informe e salve o IP Tailscale antes de copiar o comando.");
      tailscaleInputRef.current?.focus();
      return;
    }
    const nextCommand = buildConnectionCommand(clientId, selectedModel, shell, host);
    await navigator.clipboard.writeText(nextCommand);
    setCopiedClient(clientId);
    window.setTimeout(() => setCopiedClient(null), 2200);
  }

  return (
    <section className="connections-page" id="connections-section" aria-labelledby="connections-heading">
      <div className="page-heading connections-heading">
        <div>
          <div className="section-kicker">Conexões</div>
          <h1 id="connections-heading">Conectar seus clientes</h1>
          <p>Gere o comando pronto para usar seus clientes Ollama com o gateway configurado.</p>
        </div>
        <div className={`connection-host${gatewayRunning ? " is-running" : ""}`}>
          <span className="status-dot" aria-hidden="true" />
          Gateway {gatewayRunning ? "ativo" : "parado"} · {networkBind ? "escutando em todas as interfaces" : host}
        </div>
      </div>

      <div className="connections-toolbar">
        <label className="connection-select">
          <span>Modelo</span>
          <select aria-label="Modelo" value={selectedModel ?? ""} onChange={(event) => onSelectModel(event.target.value)}>
            <option value="" disabled>Selecione um modelo</option>
            {models.map((model) => <option key={model.name} value={model.name}>{model.name}</option>)}
          </select>
        </label>
        <label className="connection-select">
          <span>Shell</span>
          <select aria-label="Shell" value={shell} onChange={(event) => setShell(event.target.value as ShellKind)}>
            <option value="posix">macOS / Linux</option>
            <option value="powershell">Windows PowerShell</option>
          </select>
        </label>
      </div>

      {networkBind && (
        <div className="connection-ip-editor">
          <label htmlFor="connection-tailscale-ip">IP Tailscale da máquina servidora</label>
          <div className="connection-ip-row">
            <input
              ref={tailscaleInputRef}
              id="connection-tailscale-ip"
              type="text"
              inputMode="text"
              value={draftTailscaleIp}
              onChange={(event) => {
                setDraftTailscaleIp(event.target.value);
                setTailscaleStatus("idle");
                setTailscaleError(null);
              }}
              placeholder="100.64.0.1"
            />
            <button type="button" onClick={() => { void saveIp(); }} disabled={tailscaleStatus === "saving"}>
              {tailscaleStatus === "saving" ? "Salvando…" : "Salvar IP"}
            </button>
          </div>
          {tailscaleError && <p className="connection-ip-feedback is-error" role="alert">{tailscaleError}</p>}
          {!tailscaleError && tailscaleStatus === "success" && <p className="connection-ip-feedback is-success" role="status">IP Tailscale salvo.</p>}
        </div>
      )}

      <div className="connection-grid" role="group" aria-label="Clientes Ollama">
        {connectionClients.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`connection-card${selectedClient === item.id ? " is-selected" : ""}`}
            aria-pressed={selectedClient === item.id}
            onClick={() => { setSelectedClient(item.id); void copyCommand(item.id); }}
          >
            <span className="connection-card-mark"><ConnectionIcon id={item.id} /></span>
            <span className="connection-card-copy">
              <strong>{item.label}</strong>
              <small>{item.description}</small>
            </span>
            <span className="connection-card-state">{copiedClient === item.id ? "Copiado" : "Copiar"}</span>
          </button>
        ))}
      </div>

      <div className="connection-guidance" role="status" aria-live="polite">
        <span className="connection-guidance-mark"><ConnectionIcon id={selectedClient} /></span>
        <div>
          <strong>{copiedClient ? `Comando do ${client.label} copiado` : "Clique em um card para copiar o comando"}</strong>
          <p>{selectedModel ? `Modelo ${selectedModel} · ${networkBind ? savedTailscaleIp ? gatewayUrlForIp(savedTailscaleIp, gateway.port) : "salve o IP Tailscale da máquina servidora" : host}` : "Selecione um modelo antes de copiar um comando."}</p>
        </div>
        {!gatewayRunning && <span className="connection-warning"><span className="status-dot" aria-hidden="true" /> Gateway parada</span>}
      </div>
      <span className="sr-only" aria-live="polite">{copiedClient ? "Comando copiado para a área de transferência" : ""}</span>
    </section>
  );
}
