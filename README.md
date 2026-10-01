# Ollama Configurator

Aplicação local para diagnóstico e configuração segura do Ollama.

## Desenvolvimento

Requisitos: Python 3.12+, `uv`, Node.js 22+ e npm. O Ollama deve estar instalado
se os fluxos de integração forem executados.

Modo recomendado de desenvolvimento (backend e frontend juntos):

```bash
uv run python scripts/dev.py
```

Isso mantém o backend em `127.0.0.1:8787` e o frontend em `127.0.0.1:5173`.

Modo manual, se necessário:

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

Para uso entre máquinas na mesma tailnet, na interface abra **Acesso do
gateway**, selecione **Rede local e Tailscale (0.0.0.0)**, salve o endereço e
clique em **Aplicar e reiniciar gateway**. O configurador mostra o estado
efetivo; depois use o IP Tailscale real do computador que executa o Ollama e
proteja o gateway com uma chave:

```bash
export OLLAMA_GATEWAY_API_KEY='defina-uma-chave-forte'
uv run uvicorn backend.gateway:app --host 0.0.0.0 --port 11435
```

O cliente remoto deverá usar `http://<IP-TAILSCALE-DO-HOST>:11435/v1` e enviar
essa chave como `x-api-key` ou Bearer token. A porta `11434` permanece interna;
não é necessário expô-la na tailnet. `0.0.0.0` é endereço de escuta, não deve
ser usado como endereço do cliente.

## Testes

```bash
uv run pytest
cd frontend && npm test -- --run
```

Veja `docs/development-setup.md` e `docs/dependencies.md` para detalhes.

## Empacotamento

O fluxo de release e os limites de instalação/desinstalação estão em
`docs/packaging.md`, `docs/uninstall.md` e `docs/release-process.md`. O
empacotamento exige PyInstaller e deve ser executado pelos scripts nativos de
`packaging/macos` ou `packaging/windows`; o uso diário continua sendo local e
não exige esses artefatos.
