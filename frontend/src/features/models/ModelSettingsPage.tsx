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
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({ ...current, [name]: name === "keep_alive" ? value : Number(value) }));
  };
  const setDefault = (name: keyof Options) => {
    setDirty(true);
    setMessage("Alterações não salvas");
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
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({
      ...current,
      [name]: current[name] ?? (name === "temperature" ? 0.7 : name === "num_ctx" ? 4096 : name === "num_predict" ? -1 : "5m"),
    }));
  };
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
    await applySettings();
    if (loadRuntime) setRuntime(await loadRuntime());
    setMessage("Configurações aplicadas");
  };

  return (
    <section aria-labelledby="settings-heading">
      <h2 id="settings-heading">Configurações de {modelId}</h2>
      <ParameterControl
        id="num_ctx"
        label="Context Window"
        value={options.num_ctx ?? ""}
        disabled={defaults.num_ctx}
        onChange={(value) => setValue("num_ctx", value)}
        onCustom={() => setCustom("num_ctx")}
        onDefault={() => setDefault("num_ctx")}
        defaultLabel={nativeDefaults.num_ctx}
        presets={[{ label: "16K", value: "16384" }, { label: "32K", value: "32768" }, { label: "64K", value: "65536" }, { label: "128K", value: "131072" }, { label: "256K", value: "262144" }]}
      />
      {thinking ? (
        <div>
          <label htmlFor="thinking">Reasoning / Thinking</label>
          <select
            id="thinking"
            value={String(thinkingValue)}
            onChange={(event) => {
              const value = event.target.value;
              setDirty(true);
              setMessage("Alterações não salvas");
              setThinkingValue(value === "default" ? "default" : value === "true" ? true : value === "false" ? false : value);
            }}
          >
            <option value="default">Ollama Default ({String(thinking.default)})</option>
            {thinking.values.map((value) => <option key={String(value)} value={String(value)}>{String(value)}</option>)}
          </select>
        </div>
      ) : null}
      <ParameterControl
        id="temperature"
        label="Temperature"
        value={options.temperature ?? ""}
        disabled={defaults.temperature}
        onChange={(value) => setValue("temperature", value)}
        onCustom={() => setCustom("temperature")}
        onDefault={() => setDefault("temperature")}
        defaultLabel={nativeDefaults.temperature}
        presets={[{ label: "0", value: "0" }, { label: "0.2", value: "0.2" }, { label: "0.7", value: "0.7" }, { label: "1.0", value: "1.0" }]}
      />
      <ParameterControl
        id="num_predict"
        label="Max Output Tokens"
        value={options.num_predict ?? ""}
        disabled={defaults.num_predict}
        onChange={(value) => setValue("num_predict", value)}
        onCustom={() => setCustom("num_predict")}
        onDefault={() => setDefault("num_predict")}
        defaultLabel={nativeDefaults.num_predict}
        presets={[{ label: "512", value: "512" }, { label: "1K", value: "1024" }, { label: "2K", value: "2048" }, { label: "4K", value: "4096" }, { label: "8K", value: "8192" }]}
      />
      <ParameterControl
        id="keep_alive"
        label="Keep Alive"
        type="text"
        value={options.keep_alive ?? ""}
        disabled={defaults.keep_alive}
        onChange={(value) => setValue("keep_alive", value)}
        onCustom={() => setCustom("keep_alive")}
        onDefault={() => setDefault("keep_alive")}
        defaultLabel={nativeDefaults.keep_alive}
        presets={[{ label: "5m", value: "5m" }, { label: "30m", value: "30m" }, { label: "1h", value: "1h" }]}
      />
      <button type="button" onClick={save}>Salvar</button>
      <button type="button" onClick={apply}>Aplicar no Ollama</button>
      {message ? <p role="status">{message}</p> : null}
      {runtime ? <RuntimeStatus runtime={runtime} /> : null}
    </section>
  );
}
