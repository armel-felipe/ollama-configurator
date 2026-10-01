---
name: ollama-terminal-command
description: Gere o comando de terminal para executar um modelo Ollama através do gateway gerenciado deste projeto. Use sempre que o usuário pedir para rodar ollama no terminal, configurar OLLAMA_HOST, testar o gateway na porta 11435, usar --verbose, testar via OpenCode ou verificar se um cliente Ollama passa pelo controlador. Não crie uma feature na aplicação para isso.
---

# Comando Ollama pelo gateway

Esta skill transforma o modelo escolhido e o endereço do gateway em um comando
pronto para copiar e colar. O objetivo é fazer o cliente Ollama passar pela
porta gerenciada do projeto, preservando o perfil aplicado pelo gateway.

## Pré-condições

1. Confirme no estado da aplicação ou na documentação do projeto qual gateway
   está ativo e qual porta ele usa.
2. O padrão local deste projeto é `http://127.0.0.1:11435`.
3. Para outro computador na rede Tailscale, use o IP Tailscale da máquina que
   hospeda o gateway, por exemplo `http://100.x.y.z:11435`.
4. Não use `11434` quando a intenção for passar pelo controlador.
5. Não invente o nome do modelo: use o nome informado pelo usuário ou um nome
   confirmado na lista de modelos instalados.

## Saída obrigatória para macOS/Linux

Entregue duas linhas separadas, exatamente nesta ordem. A primeira linha deve
definir `OLLAMA_HOST` e a segunda deve executar o modelo. Não combine a variável
de ambiente com `ollama run` na mesma linha:

```bash
export OLLAMA_HOST=http://127.0.0.1:11435
ollama run <modelo> --verbose
```

O `--verbose` deve ficar no final da segunda linha. Não use barra invertida
para unir as duas linhas.

## Saída para Windows PowerShell

Quando o usuário estiver no Windows, entregue:

```powershell
$env:OLLAMA_HOST="http://127.0.0.1:11435"
ollama run <modelo> --verbose
```

Se for útil, informe que a variável vale para a sessão atual do PowerShell.

## Tailscale

Para um cliente remoto, substitua somente o host:

```bash
export OLLAMA_HOST=http://<IP-TAILSCALE-DO-HOST>:11435
ollama run <modelo> --verbose
```

Avise que isso exige o gateway escutando em um endereço acessível pelo
Tailscale, além de firewall e autenticação configurados conforme a
documentação de segurança. Não recomende expor `0.0.0.0` sem explicar o risco.

## Diagnóstico de erro

- `400 Bad Request`: confirme se o gateway está realmente ativo em `11435`,
  se o modelo existe e se as duas linhas foram executadas na mesma sessão do
  Terminal.
- `connection refused`: o gateway não está escutando nesse host/porta; peça
  para o usuário iniciar o gateway pela aplicação ou pelo launcher.
- Se `ollama run` funcionar em `11434` mas não em `11435`, o primeiro teste é
  consultar o status da gateway e não alterar parâmetros do modelo.
- Explique que uma sessão interativa aberta antes da mudança pode manter seu
  próprio estado; encerre e abra uma nova sessão para testar a configuração
  atual.

## Forma da resposta

Se o usuário só pedir “como rodo”, seja direto:

1. uma frase dizendo que o gateway precisa estar ativo;
2. o comando completo em bloco de código;
3. uma frase curta sobre o host remoto, se Tailscale estiver em escopo.

Não proponha uma alteração de UI nem execute o comando no computador do
usuário sem autorização explícita.
