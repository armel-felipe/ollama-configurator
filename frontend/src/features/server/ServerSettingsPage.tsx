import { useCallback, useEffect, useMemo, useState } from "react";
import type { ServerRestartResult, ServerSettingsState } from "../../api/client";

type Value = string | number | boolean;
type Props = {
  load: () => Promise<ServerSettingsState>;
  update: (patch: Record<string, Value | "default">) => Promise<ServerSettingsState>;
  restart: () => Promise<ServerRestartResult>;
  reset: () => Promise<ServerSettingsState>;
  restartApplication: () => Promise<void>;
};

export function ServerSettingsPage({ load, update, restart, reset, restartApplication }: Props) {
  const [state, setState] = useState<ServerSettingsState | null>(null);
  const [values, setValues] = useState<Record<string, Value>>({});
  const [defaults, setDefaults] = useState<Set<string>>(new Set());
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [confirmRestart, setConfirmRestart] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setError(null);
    void load().then((next) => {
      setState(next);
      setValues({ ...next.effective, ...next.settings });
      setDefaults(new Set());
      setDirty(false);
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Falha ao carregar configurações globais"));
  }, [load]);

  useEffect(() => { refresh(); }, [refresh]);

  const entries = useMemo(() => Object.entries(state?.capabilities ?? {}), [state]);
  const restartApp = async () => {
    setBusy(true);
    try {
      await restartApplication();
      window.setTimeout(() => window.location.reload(), 1200);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Falha ao reiniciar a aplicação");
      setBusy(false);
    }
  };
  if (error) return <section aria-labelledby="server-settings-heading"><h2 id="server-settings-heading">Configurações globais do Ollama</h2><p className="server-error" aria-live="polite">{error}</p><div className="server-recovery-actions"><button type="button" onClick={refresh}>Recarregar configurações globais</button><button type="button" onClick={() => void restartApp()} disabled={busy}>Reiniciar aplicação</button></div></section>;
  if (!state) return <section aria-labelledby="server-settings-heading"><h2 id="server-settings-heading">Configurações globais do Ollama</h2><p>Carregando configurações do servidor…</p></section>;

  const change = (name: string, value: Value) => {
    setValues((current) => ({ ...current, [name]: value }));
    setDefaults((current) => { const next = new Set(current); next.delete(name); return next; });
    setDirty(true);
    setMessage(null);
  };
  const markDefault = (name: string) => {
    setDefaults((current) => new Set(current).add(name));
    setValues((current) => ({ ...current, [name]: state.effective[name] }));
    setDirty(true);
    setMessage(null);
  };
  const save = async () => {
    setBusy(true); setError(null);
    try {
      const patch: Record<string, Value | "default"> = {};
      entries.forEach(([name]) => { patch[name] = defaults.has(name) ? "default" : values[name]; });
      const next = await update(patch);
      setState(next); setValues({ ...next.effective, ...next.settings }); setDefaults(new Set()); setDirty(false); setMessage("Configurações globais salvas; reinício pendente");
    } catch (reason: unknown) { setError(reason instanceof Error ? reason.message : "Falha ao salvar configurações globais"); }
    finally { setBusy(false); }
  };
  const runRestart = async () => {
    setBusy(true); setError(null); setConfirmRestart(false);
    try { const result = await restart(); setMessage(result.success ? `${result.detail}. Perfis reaplicados: ${result.reapplied_models.length ? result.reapplied_models.join(", ") : "nenhum modelo carregado"}` : result.detail); refresh(); }
    catch (reason: unknown) { setError(reason instanceof Error ? reason.message : "Falha ao reiniciar o Ollama"); }
    finally { setBusy(false); }
  };
  const runReset = async () => {
    setBusy(true); setError(null);
    try { const next = await reset(); setState(next); setValues({ ...next.effective }); setDefaults(new Set()); setDirty(false); setMessage("Configurações restauradas; reinício pendente"); }
    catch (reason: unknown) { setError(reason instanceof Error ? reason.message : "Falha ao restaurar configurações globais"); }
    finally { setBusy(false); }
  };

  return (
    <section className="server-settings-page" aria-labelledby="server-settings-heading">
      <div className="page-heading">
        <div><div className="section-kicker">Servidor</div><h2 id="server-settings-heading">Configurações globais do Ollama</h2><p>Defina valores usados por qualquer modelo e cliente que passe pelo runtime gerenciado.</p></div>
        <div className="server-heading-actions"><span className={`server-availability ${state.available ? "is-available" : ""}`}>{state.available ? "Servidor disponível" : "Servidor indisponível"}</span><button type="button" onClick={() => void restartApp()} disabled={busy}>Reiniciar aplicação</button></div>
      </div>
      {state.pending_restart ? <p className="pending-banner" role="status">Reinício pendente: as mudanças serão aplicadas ao reiniciar o Ollama.</p> : null}
      <div className="server-settings-grid">
        {entries.map(([name, capability]) => (
          <article className="server-setting-card" key={name}>
            <div><h3>{capability.label}</h3><p>{capability.description}</p></div>
            {capability.type === "select" ? <select aria-label={capability.label} value={String(values[name])} onChange={(event) => change(name, event.target.value)}>{capability.options?.map((option) => <option key={option} value={option}>{option}</option>)}</select> : null}
            {capability.type === "boolean" ? <label className="server-switch"><input type="checkbox" aria-label={capability.label} checked={values[name] === true} onChange={(event) => change(name, event.target.checked)} /><span>{values[name] === true ? "Ligado" : "Desligado"}</span></label> : null}
            {capability.type === "number" || capability.type === "text" ? <input aria-label={capability.label} type={capability.type === "number" ? "number" : "text"} min={capability.min} value={String(values[name])} onChange={(event) => change(name, capability.type === "number" ? Number(event.target.value) : event.target.value)} /> : null}
            <button className="default-toggle" type="button" onClick={() => markDefault(name)}>Ollama Default</button>
            <small>Efetivo agora: {String(state.effective[name])}</small>
          </article>
        ))}
      </div>
      <div className="server-actions">
        <span>{dirty ? "Alterações não salvas" : message ?? "Perfil global salvo"}</span>
        <div><button type="button" onClick={() => void runReset()} disabled={busy}>Restaurar padrões</button><button type="button" onClick={() => setConfirmRestart(true)} disabled={busy || state.pending_restart === false}>Reiniciar Ollama</button><button className="primary-action" type="button" onClick={() => void save()} disabled={busy || !dirty}>Salvar configurações</button></div>
      </div>
      {error ? <p role="alert">{error}</p> : null}
      {confirmRestart ? <div className="restart-confirm" role="dialog" aria-labelledby="restart-title"><h3 id="restart-title">Reiniciar o Ollama?</h3><p>O servidor será reiniciado e os perfis salvos dos modelos serão reaplicados.</p><button type="button" onClick={() => setConfirmRestart(false)}>Cancelar</button><button className="primary-action" type="button" onClick={() => void runRestart()}>Confirmar reinício</button></div> : null}
    </section>
  );
}
