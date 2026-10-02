import { useCallback, useEffect, useState } from "react";
import type { GatewaySettings, GatewayStatus } from "../../api/client";

type Props = {
  getStatus: () => Promise<GatewayStatus>;
  start: () => Promise<GatewayStatus>;
  stop: () => Promise<GatewayStatus>;
  restart: () => Promise<GatewayStatus>;
  releaseExternal: () => Promise<GatewayStatus>;
  getSettings?: () => Promise<GatewaySettings>;
  updateSettings?: (host: string) => Promise<GatewaySettings>;
  updateTailscaleIp?: (ip: string) => Promise<GatewaySettings>;
  applySettings?: () => Promise<{ status: GatewayStatus; settings: GatewaySettings }>;
  onStateChange?: (status: GatewayStatus, error: string | null, bindPending?: boolean) => void;
};

function statusLabel(state: GatewayStatus["state"]): string {
  return {
    stopped: "Parado",
    starting: "Iniciando",
    running: "Ativo — respondendo",
    external: "Processo externo",
    error: "Erro",
  }[state];
}

export function GatewayControls({ getStatus, start, stop, restart, releaseExternal, getSettings, updateSettings, updateTailscaleIp, applySettings, onStateChange }: Props) {
  const [status, setStatus] = useState<GatewayStatus | null>(null);
  const [settings, setSettings] = useState<GatewaySettings | null>(null);
  const [bindHost, setBindHost] = useState<string>("127.0.0.1");
  const [tailscaleIp, setTailscaleIp] = useState("");
  const [tailscaleIpDirty, setTailscaleIpDirty] = useState(false);
  const [bindDirty, setBindDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [settingsBusy, setSettingsBusy] = useState(false);
  const [confirmRelease, setConfirmRelease] = useState(false);

  const load = useCallback(() => {
    void getStatus().then((next) => {
      setStatus(next);
      setError(null);
      onStateChange?.(next, null);
    }).catch((reason: unknown) => {
      const message = reason instanceof Error ? reason.message : "Falha ao consultar a gateway";
      setError(message);
    });
  }, [getStatus, onStateChange]);

  useEffect(() => { load(); }, [load]);
  const loadSettings = useCallback(async () => {
    if (!getSettings) return;
    setSettingsError(null);
    try {
      const next = await getSettings();
      setSettings(next);
      setBindHost(next.host);
      setTailscaleIp(next.tailscale_ip ?? "");
      setTailscaleIpDirty(false);
      setBindDirty(false);
      setSettingsMessage(null);
    } catch (reason: unknown) {
      setSettingsError(reason instanceof Error ? reason.message : "Falha ao carregar o acesso do gateway");
    }
  }, [getSettings]);

  useEffect(() => { void loadSettings(); }, [loadSettings]);
  useEffect(() => {
    if (status) onStateChange?.(status, error, bindDirty || Boolean(settings?.pending_restart));
  }, [bindDirty, error, onStateChange, settings?.pending_restart, status]);
  useEffect(() => {
    if (status?.state !== "starting" && status?.state !== "running") return undefined;
    const timer = window.setInterval(load, status.state === "starting" ? 1000 : 5000);
    return () => window.clearInterval(timer);
  }, [load, status?.state]);

  const action = async (operation: () => Promise<GatewayStatus>) => {
    setBusy(true);
    setError(null);
    try {
      const next = await operation();
      setStatus(next);
      onStateChange?.(next, null);
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : "Falha ao controlar a gateway";
      setError(message);
      if (status) onStateChange?.(status, message);
    } finally {
      setBusy(false);
    }
  };

  const saveBind = async () => {
    if (!updateSettings) return;
    setSettingsBusy(true);
    setSettingsError(null);
    try {
      const next = await updateSettings(bindHost);
      setSettings(next);
      setBindHost(next.host);
      setBindDirty(false);
      setSettingsMessage("Endereço salvo; aplicação pendente");
    } catch (reason: unknown) {
      setSettingsError(reason instanceof Error ? reason.message : "Falha ao salvar o acesso do gateway");
    } finally {
      setSettingsBusy(false);
    }
  };

  const applyBind = async () => {
    if (!applySettings) return;
    setSettingsBusy(true);
    setSettingsError(null);
    try {
      const result = await applySettings();
      setStatus(result.status);
      setSettings(result.settings);
      setBindHost(result.settings.host);
      setBindDirty(false);
      setSettingsMessage(result.status.state === "starting" ? "Gateway reiniciando…" : "Gateway ativo com o novo endereço");
      onStateChange?.(result.status, null);
    } catch (reason: unknown) {
      setSettingsError(reason instanceof Error ? reason.message : "Falha ao aplicar o acesso do gateway");
    } finally {
      setSettingsBusy(false);
    }
  };

  const saveTailscaleIp = async () => {
    if (!updateTailscaleIp) return;
    setSettingsBusy(true);
    setSettingsError(null);
    try {
      const next = await updateTailscaleIp(tailscaleIp.trim());
      setSettings(next);
      setTailscaleIp(next.tailscale_ip ?? "");
      setTailscaleIpDirty(false);
      setSettingsMessage("IP Tailscale salvo.");
    } catch (reason: unknown) {
      setSettingsError(reason instanceof Error ? reason.message : "Falha ao salvar o IP Tailscale");
    } finally {
      setSettingsBusy(false);
    }
  };

  if (!status) return <section aria-labelledby="gateway-heading"><h2 id="gateway-heading">Runtime Gateway</h2><p>Consultando servidor…</p></section>;

  const unmanaged = status.state === "external";
  return (
    <section id="gateway-section" aria-labelledby="gateway-heading">
      <h2 id="gateway-heading">Runtime Gateway</h2>
      <p>Status: <strong>{statusLabel(status.state)}</strong></p>
      <p>Porta: {status.port}</p>
      {status.host === "0.0.0.0" ? (
        <p>Bind: todas as interfaces · porta {status.port}</p>
      ) : (
        <p>Local: http://{status.host}:{status.port}</p>
      )}
      {status.pid ? <p>PID: {status.pid}</p> : null}
      {unmanaged ? <><p>O processo externo {status.process ? <strong>{status.process}</strong> : "identificado"} está usando a porta.</p><p>Libere a porta para iniciar o gateway gerenciado.</p>{confirmRelease ? <div role="alert"><p>Encerrar o processo externo pode interromper outro serviço. Confirme para continuar.</p><button type="button" onClick={() => setConfirmRelease(false)}>Cancelar</button><button type="button" onClick={() => void action(releaseExternal)}>Confirmar encerramento</button></div> : <button type="button" onClick={() => setConfirmRelease(true)} disabled={busy}>Liberar porta</button>}</> : null}
      {status.detail && !unmanaged ? <p>{status.detail}</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {getSettings ? (
        <div className="gateway-access-panel">
          <div>
            <h3>Acesso do gateway</h3>
            <p>Escolha onde o gateway escuta. A porta permanece {status.port}.</p>
          </div>
          {settingsError ? (
            <div className="gateway-settings-error" role="alert">
              <p>{settingsError}</p>
              <button type="button" onClick={() => void loadSettings()} disabled={settingsBusy}>Recarregar acesso do gateway</button>
            </div>
          ) : settings ? (
            <>
              <label className="gateway-bind-select">
                <span>Endereço de escuta do gateway</span>
                <select value={bindHost} onChange={(event) => { setBindHost(event.target.value); setBindDirty(true); setSettingsMessage(null); }} disabled={settingsBusy}>
                  <option value="127.0.0.1">Somente esta máquina (127.0.0.1)</option>
                  <option value="0.0.0.0">Rede local e Tailscale (0.0.0.0)</option>
                </select>
              </label>
              {bindHost === "0.0.0.0" ? <p className="gateway-network-warning" role="alert">{settings.warning ?? "O gateway ficará acessível pelas interfaces de rede desta máquina. Use apenas em uma rede confiável e considere configurar uma chave de API."}</p> : null}
              {bindHost === "0.0.0.0" && updateTailscaleIp ? (
                <div className="gateway-tailscale-ip">
                  <label htmlFor="gateway-tailscale-ip">IP Tailscale da máquina servidora</label>
                  <div className="gateway-tailscale-ip-row">
                    <input
                      id="gateway-tailscale-ip"
                      type="text"
                      inputMode="text"
                      value={tailscaleIp}
                      placeholder="100.64.0.1"
                      onChange={(event) => { setTailscaleIp(event.target.value); setTailscaleIpDirty(true); setSettingsMessage(null); setSettingsError(null); }}
                    />
                    <button type="button" onClick={() => void saveTailscaleIp()} disabled={settingsBusy || !tailscaleIpDirty}>Salvar IP</button>
                  </div>
                </div>
              ) : null}
              <p className="gateway-effective-state">Salvo: <strong>{settings.host}</strong> · Efetivo agora: <strong>{settings.effective_host}</strong>{settings.pending_restart ? " · aplicação pendente" : ""}</p>
              {bindDirty ? <p className="gateway-settings-message" role="status">Alteração não salva</p> : null}
              {!bindDirty && settingsMessage ? <p className="gateway-settings-message" role="status">{settingsMessage}</p> : null}
              <div className="gateway-settings-actions">
                <button type="button" onClick={() => void saveBind()} disabled={settingsBusy || !bindDirty}>Salvar endereço</button>
                <button className="primary-action" type="button" onClick={() => void applyBind()} disabled={settingsBusy || bindDirty || !settings.pending_restart}>Aplicar e reiniciar gateway</button>
              </div>
              {bindHost === "0.0.0.0" ? <small className="gateway-remote-hint">Para outro dispositivo, use o IP Tailscale desta máquina com a porta {status.port}; 0.0.0.0 é apenas o endereço de escuta.</small> : null}
            </>
          ) : <p>Carregando acesso do gateway…</p>}
        </div>
      ) : null}
      {!unmanaged && status.state !== "running" ? (
        <button type="button" onClick={() => void action(start)} disabled={busy || status.state === "starting"}>
          Iniciar gateway
        </button>
      ) : null}
      {status.state === "running" ? (
        <>
          <button type="button" onClick={() => void action(stop)} disabled={busy}>Parar gateway</button>
          <button type="button" onClick={() => void action(restart)} disabled={busy}>Reiniciar gateway</button>
        </>
      ) : null}
    </section>
  );
}
