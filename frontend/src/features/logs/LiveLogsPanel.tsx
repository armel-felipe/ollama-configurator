import { useEffect, useMemo, useState } from "react";

export type LogEvent = {
  timestamp: string;
  service: "configurator" | "gateway" | "ollama" | string;
  level: "info" | "warning" | "error" | string;
  message: string;
  metadata: Record<string, unknown>;
};

type Props = {
  load?: () => Promise<LogEvent[]>;
  subscribe?: (onEvent: (event: LogEvent) => void, onConnection: (connected: boolean) => void) => () => void;
};

const filters = [
  ["all", "Todos"],
  ["configurator", "Configurator"],
  ["gateway", "Gateway"],
  ["ollama", "Ollama"],
] as const;

const defaultLoad = async (): Promise<LogEvent[]> => {
  const response = await fetch("/api/logs");
  if (!response.ok) throw new Error("Não foi possível carregar os logs");
  return response.json() as Promise<LogEvent[]>;
};

const defaultSubscribe: NonNullable<Props["subscribe"]> = (onEvent, onConnection) => {
  if (typeof EventSource === "undefined") {
    onConnection(false);
    return () => undefined;
  }
  const source = new EventSource("/api/logs/stream");
  source.onopen = () => onConnection(true);
  source.onmessage = (event) => onEvent(JSON.parse(event.data) as LogEvent);
  source.onerror = () => onConnection(false);
  return () => source.close();
};

function formatMetadata(metadata: Record<string, unknown>): string {
  const entries = Object.entries(metadata).filter(([, value]) => value !== undefined && value !== null);
  return entries.length ? ` · ${entries.map(([key, value]) => `${key}=${String(value)}`).join(" · ")}` : "";
}

export function LiveLogsPanel({ load = defaultLoad, subscribe = defaultSubscribe }: Props) {
  const [events, setEvents] = useState<LogEvent[]>([]);
  const [filter, setFilter] = useState<(typeof filters)[number][0]>("all");
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void load().then((next) => {
      if (active) setEvents(next.slice(-200));
    }).catch((reason: unknown) => {
      if (active) setError(reason instanceof Error ? reason.message : "Não foi possível carregar os logs");
    });
    const unsubscribe = subscribe((event) => {
      if (active) setEvents((current) => [...current, event].slice(-200));
    }, setConnected);
    return () => { active = false; unsubscribe(); };
  }, [load, subscribe]);

  const visibleEvents = useMemo(
    () => filter === "all" ? events : events.filter((event) => event.service === filter),
    [events, filter],
  );

  return (
    <section className="live-logs-panel" aria-labelledby="live-logs-heading">
      <div className="page-heading">
        <div><h2 id="live-logs-heading">Logs em tempo real</h2><p>Eventos técnicos do Configurator, Gateway e Ollama. O conteúdo interno do raciocínio não é registrado.</p></div>
        <span className={`logs-connection ${connected ? "is-live" : ""}`} role="status">{connected ? "Ao vivo" : "Desconectado"}</span>
      </div>
      <div className="logs-toolbar" aria-label="Filtros de logs">
        <div className="logs-filters" role="group" aria-label="Filtrar logs">
          {filters.map(([value, label]) => <button key={value} className={filter === value ? "is-selected" : ""} type="button" onClick={() => setFilter(value)}>{label}</button>)}
        </div>
        <button type="button" onClick={() => setEvents([])}>Limpar visualização</button>
      </div>
      {error ? <p className="logs-error" role="status">{error}</p> : null}
      <div className="logs-list" role="log" aria-live="polite">
        {visibleEvents.length ? visibleEvents.map((event, index) => <div className={`log-entry log-${event.level}`} key={`${event.timestamp}-${index}`}><time>{new Date(event.timestamp).toLocaleTimeString()}</time><strong>{event.service}</strong><span>{event.message}{formatMetadata(event.metadata)}</span></div>) : <p className="logs-empty">Aguardando eventos…</p>}
      </div>
    </section>
  );
}
