import type { RuntimeStatus as RuntimeStatusData } from "../../api/client";

export function RuntimeStatus({ runtime }: { runtime: RuntimeStatusData }) {
  const context = runtime.context ? `${Math.round(runtime.context / 1024)}K` : "não observado";
  return (
    <section aria-labelledby="runtime-heading">
      <h3 id="runtime-heading">Runtime efetivo</h3>
      <p>{runtime.loaded ? "Modelo carregado" : "Modelo não carregado"}</p>
      <p>Contexto: {context}</p>
      {runtime.processor ? <p>Processador: {runtime.processor}</p> : null}
      <p>Thinking aplicado: {String(runtime.applied_options.think ?? "Ollama Default")}</p>
    </section>
  );
}
