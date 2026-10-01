import { useState } from "react";
import type { InferenceTestResult } from "../../api/client";

type Props = {
  modelId: string;
  runInference: (prompt: string) => Promise<InferenceTestResult>;
};

function formatThinking(value: boolean | string | number | undefined): string {
  if (value === undefined) return "Ollama Default";
  return String(value);
}

export function InferenceTestPanel({ modelId, runInference }: Props) {
  const [prompt, setPrompt] = useState("Quem foi o 23º presidente do Brasil?");
  const [result, setResult] = useState<InferenceTestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const execute = async () => {
    setRunning(true);
    setError(null);
    try {
      setResult(await runInference(prompt));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Falha no teste de inferência");
    } finally {
      setRunning(false);
    }
  };

  const requestedThinking = result?.requested_profile.think;
  const context = result?.runtime.context;

  return (
    <section aria-labelledby="inference-test-heading">
      <h2 id="inference-test-heading">Teste de inferência de {modelId}</h2>
      <p>
        Este teste usa o perfil salvo pela aplicação em cada requisição. Uma sessão externa do
        <code> ollama run </code> é independente e não recebe estas configurações.
      </p>
      <label htmlFor="inference-prompt">Prompt de teste</label>
      <textarea
        id="inference-prompt"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        rows={3}
      />
      <button type="button" onClick={execute} disabled={running || !prompt.trim()}>
        {running ? "Executando…" : "Executar teste"}
      </button>
      {error ? <p role="alert">{error}</p> : null}
      {result ? (
        <div aria-live="polite">
          <p>Thinking solicitado: {formatThinking(requestedThinking)}</p>
          <p>Thinking recebido: {result.thinking_received ? "sim" : "não"}</p>
          <p>Contexto efetivo: {context ? `${Math.round(context / 1024)}K` : "não observado"}</p>
          {result.thinking ? (
            <details open>
              <summary>Thinking retornado</summary>
              <pre>{result.thinking}</pre>
            </details>
          ) : null}
          <h3>Resposta final</h3>
          <p>{result.response}</p>
        </div>
      ) : null}
    </section>
  );
}
