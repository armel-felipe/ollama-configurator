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
    <section className="models-list" aria-labelledby="models-heading">
      <div className="section-heading">
        <div>
          <div className="section-kicker">Biblioteca</div>
          <h2 id="models-heading">Modelos instalados</h2>
        </div>
        <span className="model-count">{models.length}</span>
      </div>
      {models.length === 0 ? (
        <p className="empty-copy">Nenhum modelo instalado. Atualize a descoberta para verificar novamente.</p>
      ) : (
        <ul className="model-list">
          {models.map((model) => (
            <li key={model.name}>
              <button className="model-row" type="button" aria-pressed={selectedModel === model.name} onClick={() => onSelect?.(model.name)}>
                <span className="model-indicator" aria-hidden="true" />
                <span className="model-name">{model.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
