import { useCallback, useEffect, useState } from "react";
import { ErrorState, LoadingState } from "../shared/StatusState";
import { ParameterControl } from "./ParameterControl";
import { RuntimeStatus } from "./RuntimeStatus";
import type { RuntimeStatus as RuntimeStatusData } from "../../api/client";

type Options = {
  num_ctx?: number;
  temperature?: number;
  num_predict?: number;
  keep_alive?: string | number;
  think?: boolean | string;
};

type ThinkingSpec = { values: Array<boolean | string>; default?: boolean | string | null };

type Props = {
  modelId: string;
  loadSettings: () => Promise<{ options: Options; thinking?: ThinkingSpec | null; defaults?: Record<string, string> }>;
  saveSettings: (options: Record<string, number | string | boolean>) => Promise<unknown>;
  applySettings: () => Promise<unknown>;
  loadRuntime?: () => Promise<RuntimeStatusData>;
};

export function ModelSettingsPage({ modelId, loadSettings, saveSettings, applySettings, loadRuntime }: Props) {
  const [options, setOptions] = useState<Options>({});
  const [defaults, setDefaults] = useState<Record<string, boolean>>({
    num_ctx: true,
    temperature: true,
    num_predict: true,
    keep_alive: true,
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [thinking, setThinking] = useState<ThinkingSpec | null>(null);
  const [thinkingValue, setThinkingValue] = useState<boolean | string | "default">("default");
  const [runtime, setRuntime] = useState<RuntimeStatusData | null>(null);
  const [nativeDefaults, setNativeDefaults] = useState<Record<string, string>>({});
  const [dirty, setDirty] = useState(false);
  const [applying, setApplying] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    void loadSettings()
      .then(({ options: loaded, thinking: loadedThinking, defaults: loadedDefaults }) => {
        setOptions(loaded);
        setThinking(loadedThinking ?? null);
        setThinkingValue(loaded.think ?? "default");
        setNativeDefaults(loadedDefaults ?? {});
        setDirty(false);
        setDefaults({
          num_ctx: loaded.num_ctx === undefined,
          temperature: loaded.temperature === undefined,
          num_predict: loaded.num_predict === undefined,
          keep_alive: loaded.keep_alive === undefined,
        });
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Falha ao carregar configurações"))
      .finally(() => setLoading(false));
  }, [loadSettings]);

  useEffect(() => { load(); }, [load, modelId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const setValue = (name: keyof Options, value: string) => {
    setDirty(true);
    setMessage("Alterações não salvas");
    setRuntime(null);
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({ ...current, [name]: name === "keep_alive" ? value : Number(value) }));
  };
  const setDefault = (name: keyof Options) => {
    setDirty(true);
    setMessage("Alterações não salvas");
    setRuntime(null);
    setDefaults((current) => ({ ...current, [name]: true }));
    setOptions((current) => {
      const next = { ...current };
      delete next[name];
      return next;
    });
  };
  const setCustom = (name: keyof Options) => {
    setDirty(true);
    setMessage("Alterações não salvas");
    setRuntime(null);
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({
      ...current,
      [name]: current[name] ?? (name === "temperature" ? 0.7 : name === "num_ctx" ? 4096 : name === "num_predict" ? -1 : "5m"),
    }));
  };
  const booleanThinking = thinking?.values.every((value) => typeof value === "boolean") ?? false;
  const save = async () => {
    const patch: Record<string, number | string | boolean> = {};
    (Object.keys(defaults) as Array<keyof Options>).forEach((name) => {
      patch[name] = defaults[name] ? "default" : (options[name] as number | string);
    });
    if (thinking) patch.think = thinkingValue === "default" ? "default" : thinkingValue;
    await saveSettings(patch);
    setDirty(false);
    setMessage("Configurações salvas");
  };
  const apply = async () => {
    if (dirty) {
      setMessage("Salve as alterações antes de aplicar");
      return;
    }
    setApplying(true);
    setMessage("Aplicando no Ollama…");
    try {
      const result = await applySettings() as { runtime?: RuntimeStatusData };
      const observed = result.runtime ?? (loadRuntime ? await loadRuntime() : undefined);
      if (observed) {
        setRuntime(observed);
        const context = observed.context ? `${Math.round(observed.context / 1024)}K` : null;
        const requested = observed.requested_context
          ? `${Math.round(observed.requested_context / 1024)}K`
          : null;
        if (observed.context_matches === false && requested && context) {
          setMessage(`Aplicação não confirmada: solicitado ${requested}, efetivo ${context}`);
        } else {
          setMessage(context ? `Runtime confirmado: ${context}` : "Configurações aplicadas; runtime não observado");
        }
      } else {
        setMessage("Configurações aplicadas; runtime não observado");
      }
    } catch (reason: unknown) {
      setMessage(reason instanceof Error ? reason.message : "Falha ao aplicar configurações");
    } finally {
      setApplying(false);
    }
  };

  return (
    <section className="profile-editor" aria-labelledby="settings-heading">
      <div className="profile-header">
        <div>
          <div className="section-kicker">Perfil do modelo</div>
          <h2 id="settings-heading">{modelId}</h2>
          <p>Defina os parâmetros que serão usados quando este modelo for carregado.</p>
        </div>
        {runtime?.context_matches === true ? <span className="applied-badge">APLICADO</span> : null}
      </div>
      <div className="profile-section">
        <div className="section-heading">
          <h3>Contexto</h3>
          <p>Quanto da conversa o modelo consegue manter em memória.</p>
        </div>
        <ParameterControl
          id="num_ctx"
          label="Janela de contexto"
          value={options.num_ctx ?? ""}
          disabled={defaults.num_ctx}
          onChange={(value) => setValue("num_ctx", value)}
          onCustom={() => setCustom("num_ctx")}
          onDefault={() => setDefault("num_ctx")}
          defaultLabel={nativeDefaults.num_ctx}
          radioPresets
          presets={[{ label: "16K", value: "16384" }, { label: "32K", value: "32768" }, { label: "64K", value: "65536" }, { label: "128K", value: "131072" }, { label: "256K", value: "262144" }]}
        />
      </div>
      {thinking ? (
        <div className="profile-section">
          <div className="section-heading">
            <h3>Reasoning / Thinking</h3>
            <p>Controle se o modelo deve usar raciocínio explícito antes da resposta.</p>
          </div>
          {booleanThinking ? (
            <label className="switch-control">
              <input
                type="checkbox"
                aria-label="Thinking"
                checked={thinkingValue === true}
                onChange={(event) => {
                  setDirty(true);
                  setMessage("Alterações não salvas");
                  setRuntime(null);
                  setThinkingValue(event.target.checked);
                }}
              />
              <span className="switch-track" aria-hidden="true"><span /></span>
              <span><strong>{thinkingValue === true ? "Ligado" : "Desligado"}</strong><small>Valor booleano enviado ao Ollama</small></span>
            </label>
          ) : (
            <label className="select-control" htmlFor="thinking-level">
              <span>Nível disponível</span>
              <select
                id="thinking-level"
                value={String(thinkingValue)}
                onChange={(event) => {
                  const value = event.target.value;
                  setDirty(true);
                  setMessage("Alterações não salvas");
                  setRuntime(null);
                  setThinkingValue(value === "default" ? "default" : value === "true" ? true : value === "false" ? false : value);
                }}
              >
                <option value="default">Ollama Default ({String(thinking.default)})</option>
                {thinking.values.map((value) => <option key={String(value)} value={String(value)}>{String(value)}</option>)}
              </select>
            </label>
          )}
        </div>
      ) : null}
      <details className="profile-section advanced-section">
        <summary>Parâmetros avançados</summary>
        <div className="advanced-grid">
          <ParameterControl id="temperature" label="Temperature" value={options.temperature ?? ""} disabled={defaults.temperature} onChange={(value) => setValue("temperature", value)} onCustom={() => setCustom("temperature")} onDefault={() => setDefault("temperature")} defaultLabel={nativeDefaults.temperature} presets={[{ label: "0", value: "0" }, { label: "0.2", value: "0.2" }, { label: "0.7", value: "0.7" }, { label: "1.0", value: "1.0" }]} />
          <ParameterControl id="num_predict" label="Max Output Tokens" value={options.num_predict ?? ""} disabled={defaults.num_predict} onChange={(value) => setValue("num_predict", value)} onCustom={() => setCustom("num_predict")} onDefault={() => setDefault("num_predict")} defaultLabel={nativeDefaults.num_predict} presets={[{ label: "512", value: "512" }, { label: "1K", value: "1024" }, { label: "2K", value: "2048" }, { label: "4K", value: "4096" }, { label: "8K", value: "8192" }]} />
          <ParameterControl id="keep_alive" label="Keep Alive" type="text" value={options.keep_alive ?? ""} disabled={defaults.keep_alive} onChange={(value) => setValue("keep_alive", value)} onCustom={() => setCustom("keep_alive")} onDefault={() => setDefault("keep_alive")} defaultLabel={nativeDefaults.keep_alive} presets={[{ label: "5m", value: "5m" }, { label: "30m", value: "30m" }, { label: "1h", value: "1h" }]} />
        </div>
      </details>
      <div className="profile-actions">
        <span className="profile-state">{dirty ? "Alterações não salvas" : runtime?.context_matches === false ? "Aplicação divergente" : runtime?.context_matches === true ? "Sem alterações pendentes" : "Perfil salvo"}</span>
        <div>
          <button className="secondary-action" type="button" onClick={save} disabled={applying}>Salvar</button>
          <button className="primary-action" type="button" onClick={apply} disabled={applying}>{applying ? "Aplicando…" : runtime?.context_matches === true ? "Aplicado" : "Aplicar no Ollama"}</button>
        </div>
      </div>
      {message ? <p role="status">{message}</p> : null}
      {runtime ? <RuntimeStatus runtime={runtime} /> : null}
    </section>
  );
}
