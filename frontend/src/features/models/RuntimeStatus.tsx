import type { RuntimeStatus as RuntimeStatusData } from "../../api/client";

export function RuntimeStatus({ runtime }: { runtime: RuntimeStatusData }) {
  const context = runtime.context ? `${Math.round(runtime.context / 1024)}K` : "não observado";
  const requested = runtime.requested_context
    ? `${Math.round(runtime.requested_context / 1024)}K`
    : null;
  return (
    <section aria-labelledby="runtime-heading">
      <h3 id="runtime-heading">Runtime efetivo</h3>
      <p>{runtime.loaded ? "Modelo carregado" : "Modelo não carregado"}</p>
      <p>Contexto efetivo: {context}</p>
      {requested ? <p>Contexto solicitado: {requested}</p> : null}
      {runtime.context_matches === false ? (
        <p role="alert">Ollama não confirmou o contexto solicitado; o valor efetivo permanece diferente.</p>
      ) : null}
      {runtime.processor ? <p>Processador: {runtime.processor}</p> : null}
      <p>Thinking aplicado: {String(runtime.applied_options.think ?? "Ollama Default")}</p>
    </section>
  );
}
