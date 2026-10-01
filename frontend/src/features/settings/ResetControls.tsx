import { useState } from "react";

type Props = {
  selectedModel?: string;
  onResetAll: () => Promise<void>;
  onResetModel: (model: string) => Promise<void>;
};

export function ResetControls({ selectedModel, onResetAll, onResetModel }: Props) {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resetAll = async () => {
    if (!window.confirm("Restaurar todos os modelos para Ollama Default?")) return;
    setError(null);
    try {
      await onResetAll();
      setMessage("Todos os modelos foram restaurados para Ollama Default");
    } catch {
      setError("Não foi possível restaurar os modelos");
    }
  };
  const resetSelected = async () => {
    if (!selectedModel || !window.confirm(`Restaurar ${selectedModel} para Ollama Default?`)) return;
    setError(null);
    try {
      await onResetModel(selectedModel);
      setMessage(`${selectedModel} foi restaurado para Ollama Default`);
    } catch {
      setError(`Não foi possível restaurar ${selectedModel}`);
    }
  };

  return (
    <section aria-labelledby="reset-heading">
      <h2 id="reset-heading">Restaurar configurações</h2>
      <button type="button" onClick={resetAll}>Restaurar todos os modelos</button>
      {selectedModel ? (
        <button type="button" onClick={resetSelected}>Restaurar modelo selecionado</button>
      ) : null}
      {message ? <p role="status">{message}</p> : null}
      {error ? <p role="alert">{error}</p> : null}
    </section>
  );
}
