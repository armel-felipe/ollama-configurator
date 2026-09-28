export function ModelsList({
  models,
  selectedModel,
  onSelect,
}: {
  models: Array<{ name: string; size?: number }>;
  selectedModel?: string;
  onSelect?: (model: string) => void;
}) {
  return (
    <section aria-labelledby="models-heading">
      <h2 id="models-heading">Modelos instalados</h2>
      {models.length === 0 ? <p>Nenhum modelo encontrado.</p> : (
        <ul>
          {models.map((model) => (
            <li key={model.name}>
              <button type="button" aria-pressed={selectedModel === model.name} onClick={() => onSelect?.(model.name)}>
                {model.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
