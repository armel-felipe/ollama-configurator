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

## Gateway para clientes externos

Para que OpenCode e outros clientes usem automaticamente os perfis salvos,
inicie o gateway em uma porta separada. Localmente, ele escuta em
`127.0.0.1:11435` e encaminha para o Ollama em `127.0.0.1:11434`:

```bash
uv run uvicorn backend.gateway:app --host 127.0.0.1 --port 11435
```

Configure o cliente para usar `http://127.0.0.1:11435/v1` (OpenAI) ou
`http://127.0.0.1:11435` (API Ollama).

Para uso entre máquinas na mesma tailnet, use o IP Tailscale do computador que
executa o Ollama e proteja o gateway com uma chave:

```bash
export OLLAMA_GATEWAY_API_KEY='defina-uma-chave-forte'
uv run uvicorn backend.gateway:app --host <IP-TAILSCALE-DO-HOST> --port 11435
```

O cliente remoto deverá usar `http://<IP-TAILSCALE-DO-HOST>:11435/v1` e enviar
essa chave como `x-api-key` ou Bearer token. A porta `11434` permanece interna;
não é necessário expô-la na tailnet.

## Testes

```bash
uv run pytest
cd frontend && npm test -- --run
```

Veja `docs/development-setup.md` e `docs/dependencies.md` para detalhes.
