import type { OperationalStatus } from "./operationalStatus";

type Props = { status: OperationalStatus };

const indicators = [
  ["application", "Aplicação"],
  ["gateway", "Gateway 11435"],
  ["configuration", "Configuração"],
  ["runtime", "Runtime"],
] as const;

export function OperationalStatusSummary({ status }: Props) {
  return (
    <section className="operational-summary" aria-label="Estado operacional" aria-live="polite">
      <div className="operational-summary-heading">
        <div>
          <div className="section-kicker">Estado operacional</div>
          <h2>O que está acontecendo agora</h2>
        </div>
        {status.primaryAction ? (
          <button className="primary-action" type="button" onClick={() => void status.primaryAction?.run()}>
            {status.primaryAction.label}
          </button>
        ) : null}
      </div>
      <div className="operational-status-grid">
        {indicators.map(([key, label]) => {
          const indicator = status[key];
          return (
            <article className="operational-status-card" data-state={indicator.state} key={key}>
              <div className="operational-status-card-heading">
                <span className="status-dot" aria-hidden="true" />
                <span>{label}</span>
              </div>
              <strong>{indicator.label}</strong>
              <p>{indicator.detail}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
