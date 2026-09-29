# Ambiente de desenvolvimento

## macOS e Windows

1. Instale Python 3.12+, Node.js 22+ e Ollama.
2. Instale `uv` conforme a documentação oficial do ambiente.
3. Na raiz do projeto, execute `uv sync`.
4. Execute `cd frontend && npm ci`.
5. Inicie os dois serviços juntos com `uv run python scripts/dev.py`.
6. Abra `http://127.0.0.1:5173`.
7. Para clientes externos, inicie o gateway em `127.0.0.1:11435`:
   `uv run uvicorn backend.gateway:app --host 127.0.0.1 --port 11435`.

O botão de retry da interface apenas repete a consulta. Se o backend estiver
parado, a tela informa explicitamente que `127.0.0.1:8787` precisa ser
iniciado; o launcher acima evita esse estado no fluxo normal de desenvolvimento.

Para iniciar os processos manualmente, use:

```bash
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8787
cd frontend && npm run dev
```

Na aplicação, a seção `Runtime Gateway` permite iniciar, parar e reiniciar esse
serviço pela interface. O comando manual continua disponível para diagnóstico e
desenvolvimento, mas não é necessário para o uso normal.

O frontend é uma interface web local durante o desenvolvimento. O instalador
final será tratado em uma etapa posterior e não exige comandos Python do usuário.

## Acesso via Tailscale

O gateway é a única porta que deve ser usada por OpenCode ou por outro
computador. Para expô-lo na tailnet, inicie-o no IP Tailscale do host que roda o
Ollama e defina `OLLAMA_GATEWAY_API_KEY`. Exemplo:

```bash
OLLAMA_GATEWAY_API_KEY='defina-uma-chave-forte' \
  uv run uvicorn backend.gateway:app --host <IP-TAILSCALE-DO-HOST> --port 11435
```

No cliente remoto, use `http://<IP-TAILSCALE-DO-HOST>:11435/v1` e a mesma chave.
Ollama continua em `127.0.0.1:11434`; não exponha diretamente essa porta.

Para o cliente Ollama nativo, configure:

```bash
OLLAMA_HOST=http://<IP-TAILSCALE-DO-HOST>:11435 ollama run gemma4:26b-mlx
```

Nesse modo, `ollama run` usa o endpoint `/api/chat` da gateway e recebe o perfil
salvo pela aplicação, inclusive `think=false` e `num_ctx`.
