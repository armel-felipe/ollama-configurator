export function LoadingState() {
  return <p role="status">Carregando…</p>;
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div role="alert">
      <p>{message}</p>
      <button type="button" onClick={onRetry}>Tentar novamente</button>
    </div>
  );
}
