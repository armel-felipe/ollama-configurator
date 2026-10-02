# Ambiente de desenvolvimento

## macOS e Windows

1. Instale Python 3.12+, Node.js 22+ e Ollama.
2. Instale `uv` conforme a documentação oficial do ambiente.
3. Na raiz do projeto, execute `uv sync`.
4. Execute `cd frontend && npm ci`.
5. Inicie os dois serviços juntos com `uv run python scripts/dev.py`.
6. Abra `http://127.0.0.1:5173`.
7. Para clientes externos, use a configuração **Acesso do gateway** na UI. O
   padrão é `127.0.0.1`; selecione `0.0.0.0`, salve e aplique para escutar em
   todas as interfaces. A aplicação reinicia somente o gateway nessa troca.

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
computador. Para expô-lo na tailnet, selecione `Rede local e Tailscale
(0.0.0.0)` na UI, salve e clique em **Aplicar e reiniciar gateway**. O
endereço `0.0.0.0` é somente o bind local; clientes devem usar o IP Tailscale
real do host que roda o Ollama. Na aba **Conectar**, informe somente esse IP em
**IP Tailscale da máquina servidora** e clique em **Salvar IP**. Hostnames
MagicDNS, protocolos e portas não são aceitos. O valor fica no `config.json`
do backend — `~/Library/Application Support/Ollama Configurator/config.json`
no macOS e `%LOCALAPPDATA%\Ollama Configurator\config.json` no Windows — e
continua disponível ao alternar entre bind local e de rede. Defina
`OLLAMA_GATEWAY_API_KEY` quando houver acesso remoto:

```bash
OLLAMA_GATEWAY_API_KEY='defina-uma-chave-forte' \
  uv run uvicorn backend.gateway:app --host 0.0.0.0 --port 11435
```

No cliente remoto, use o IP salvo, por exemplo
`http://100.87.71.48:11435/v1`, e a mesma chave. Para IPv6, use colchetes, como
`http://[fd7a:115c:a1e0::1]:11435/v1`. Ollama continua em
`127.0.0.1:11434`; não exponha diretamente essa porta.

Para o cliente Ollama nativo, abra **Conectar**, escolha macOS/Linux ou Windows
e clique no card desejado. A aplicação copia o comando completo usando o IP
salvo; não é necessário substituir um marcador manualmente. Por exemplo, no
macOS/Linux:

```bash
export OLLAMA_HOST=http://100.87.71.48:11435
ollama run gemma4:26b-mlx --verbose
```

No Windows PowerShell, a primeira linha correspondente é:

```powershell
$env:OLLAMA_HOST="http://100.87.71.48:11435"
```

Nesse modo, `ollama run` usa o endpoint `/api/chat` da gateway e recebe o perfil
salvo pela aplicação, inclusive `think=false` e `num_ctx`.
