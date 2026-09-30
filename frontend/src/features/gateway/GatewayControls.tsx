import { useCallback, useEffect, useState } from "react";
import type { GatewayStatus } from "../../api/client";

type Props = {
  getStatus: () => Promise<GatewayStatus>;
  start: () => Promise<GatewayStatus>;
  stop: () => Promise<GatewayStatus>;
  restart: () => Promise<GatewayStatus>;
  releaseExternal: () => Promise<GatewayStatus>;
  onStateChange?: (status: GatewayStatus, error: string | null) => void;
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

export function GatewayControls({ getStatus, start, stop, restart, releaseExternal, onStateChange }: Props) {
  const [status, setStatus] = useState<GatewayStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
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

  if (!status) return <section aria-labelledby="gateway-heading"><h2 id="gateway-heading">Runtime Gateway</h2><p>Consultando servidor…</p></section>;

  const unmanaged = status.state === "external";
  return (
    <section id="gateway-section" aria-labelledby="gateway-heading">
      <h2 id="gateway-heading">Runtime Gateway</h2>
      <p>Status: <strong>{statusLabel(status.state)}</strong></p>
      <p>Porta: {status.port}</p>
      <p>Local: http://{status.host}:{status.port}</p>
      {status.pid ? <p>PID: {status.pid}</p> : null}
      {unmanaged ? <><p>O processo externo {status.process ? <strong>{status.process}</strong> : "identificado"} está usando a porta.</p><p>Libere a porta para iniciar o gateway gerenciado.</p>{confirmRelease ? <div role="alert"><p>Encerrar o processo externo pode interromper outro serviço. Confirme para continuar.</p><button type="button" onClick={() => setConfirmRelease(false)}>Cancelar</button><button type="button" onClick={() => void action(releaseExternal)}>Confirmar encerramento</button></div> : <button type="button" onClick={() => setConfirmRelease(true)} disabled={busy}>Liberar porta</button>}</> : null}
      {status.detail && !unmanaged ? <p>{status.detail}</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {!unmanaged && status.state !== "running" ? (
        <button type="button" onClick={() => void action(start)} disabled={busy || status.state === "starting"}>
          Iniciar servidor
        </button>
      ) : null}
      {status.state === "running" ? (
        <>
          <button type="button" onClick={() => void action(stop)} disabled={busy}>Parar servidor</button>
          <button type="button" onClick={() => void action(restart)} disabled={busy}>Reiniciar servidor</button>
        </>
      ) : null}
    </section>
  );
}
