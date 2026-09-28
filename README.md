# Ollama Configurator

Aplicação local para diagnóstico e configuração segura do Ollama.

## Desenvolvimento

Requisitos: Python 3.12+, `uv`, Node.js 22+ e npm. O Ollama deve estar instalado
se os fluxos de integração forem executados.

Backend:

```bash
uv sync
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8787 --reload
```

Frontend, em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

## Testes

```bash
uv run pytest
cd frontend && npm test -- --run
```

Veja `docs/development-setup.md` e `docs/dependencies.md` para detalhes.
