import type { ReactNode } from "react";
import { ModelsList } from "./ModelsList";

type Model = { name: string; size?: number };

type Props = {
  models: Model[];
  selectedModel?: string;
  onSelect: (model: string) => void;
  children?: ReactNode;
};

export function ModelWorkspace({ models, selectedModel, onSelect, children }: Props) {
  return (
    <div className="model-workspace">
      <aside className="model-sidebar" aria-label="Modelos instalados">
        <ModelsList models={models} selectedModel={selectedModel} onSelect={onSelect} />
      </aside>
      <section className="model-main" aria-label="Configuração do modelo">
        {selectedModel ? children : (
          <div className="workspace-empty">
            <div className="empty-mark" aria-hidden="true">◇</div>
            <h2>Selecione um modelo para configurar</h2>
            <p>Escolha um modelo instalado na lista para abrir o perfil de runtime.</p>
          </div>
        )}
      </section>
    </div>
  );
}
