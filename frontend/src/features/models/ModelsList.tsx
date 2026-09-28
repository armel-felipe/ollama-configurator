export function ModelsList({ models }: { models: Array<{ name: string; size?: number }> }) {
  return (
    <section aria-labelledby="models-heading">
      <h2 id="models-heading">Modelos instalados</h2>
      {models.length === 0 ? <p>Nenhum modelo encontrado.</p> : (
        <ul>
          {models.map((model) => <li key={model.name}>{model.name}</li>)}
        </ul>
      )}
    </section>
  );
}
