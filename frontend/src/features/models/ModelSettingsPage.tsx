import { useCallback, useEffect, useState } from "react";
import { ErrorState, LoadingState } from "../shared/StatusState";
import { ParameterControl } from "./ParameterControl";

type Options = {
  num_ctx?: number;
  temperature?: number;
  num_predict?: number;
  keep_alive?: string | number;
};

type Props = {
  modelId: string;
  loadSettings: () => Promise<{ options: Options }>;
  saveSettings: (options: Record<string, number | string>) => Promise<unknown>;
  applySettings: () => Promise<unknown>;
};

export function ModelSettingsPage({ modelId, loadSettings, saveSettings, applySettings }: Props) {
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

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    void loadSettings()
      .then(({ options: loaded }) => {
        setOptions(loaded);
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
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({ ...current, [name]: name === "keep_alive" ? value : Number(value) }));
  };
  const setDefault = (name: keyof Options) => {
    setDefaults((current) => ({ ...current, [name]: true }));
    setOptions((current) => {
      const next = { ...current };
      delete next[name];
      return next;
    });
  };
  const setCustom = (name: keyof Options) => {
    setDefaults((current) => ({ ...current, [name]: false }));
    setOptions((current) => ({
      ...current,
      [name]: current[name] ?? (name === "temperature" ? 0.7 : name === "num_ctx" ? 4096 : name === "num_predict" ? -1 : "5m"),
    }));
  };
  const save = async () => {
    const patch: Record<string, number | string> = {};
    (Object.keys(defaults) as Array<keyof Options>).forEach((name) => {
      patch[name] = defaults[name] ? "default" : (options[name] as number | string);
    });
    await saveSettings(patch);
    setMessage("Configurações salvas");
  };
  const apply = async () => {
    await applySettings();
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
      />
      <ParameterControl
        id="temperature"
        label="Temperature"
        value={options.temperature ?? ""}
        disabled={defaults.temperature}
        onChange={(value) => setValue("temperature", value)}
        onCustom={() => setCustom("temperature")}
        onDefault={() => setDefault("temperature")}
      />
      <ParameterControl
        id="num_predict"
        label="Max Output Tokens"
        value={options.num_predict ?? ""}
        disabled={defaults.num_predict}
        onChange={(value) => setValue("num_predict", value)}
        onCustom={() => setCustom("num_predict")}
        onDefault={() => setDefault("num_predict")}
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
      />
      <button type="button" onClick={save}>Salvar</button>
      <button type="button" onClick={apply}>Aplicar no Ollama</button>
      {message ? <p role="status">{message}</p> : null}
    </section>
  );
}
