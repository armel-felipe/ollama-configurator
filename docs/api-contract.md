# Contrato inicial da API

O contrato HTTP usa prefixo `/api` e é servido apenas no endereço local.

## Fundação

- `GET /api/health` retorna `{ "status": "ok", "version": string }`.
- `GET /api/models/{model_id}/settings` retorna overrides, defaults nativos e a especificação `thinking` declarada pelo modelo em `/api/show`.
- `PUT /api/models/{model_id}/settings` salva overrides básicos do modelo.
- `DELETE /api/models/{model_id}/settings/{parameter}` remove um override específico.
- `POST /api/models/{model_id}/apply` descarrega e recarrega o runner com o perfil completo e retorna o runtime observado.
- `GET /api/models/{model_id}/runtime` consulta o modelo carregado em `/api/ps` e retorna contexto, processador e perfil aplicado.
- `POST /api/models/{model_id}/inference-test` recebe `{ "prompt": string }`, envia o prompt com o perfil salvo e retorna resposta final, thinking recebido, perfil solicitado e runtime observado.

Parâmetros básicos atuais: `num_ctx`, `temperature`, `num_predict` e
`keep_alive`. Thinking é um controle adicional validado contra os valores
declarados pelo próprio modelo. O marcador `"default"` remove o override; ele
não é convertido para `0` ou `false`.

Configurações e endpoints adicionais serão adicionados junto às tarefas que os
implementam, sempre com schemas explícitos e erros estruturados.

## Verificação de inferência

O endpoint `inference-test` é o caminho verificável para confirmar o comportamento
do perfil dentro da aplicação. `think` é enviado como campo de nível superior da
requisição `/api/generate`, preservando `false`, `true` ou o nível nomeado salvo.
Se o modelo devolver thinking em um campo separado, a resposta o identifica em
`thinking`; marcadores `<think>...</think>` vazados no texto final são separados
antes da apresentação ao usuário.

Uma sessão independente aberta com `ollama run` não é controlada por este endpoint
e pode continuar usando o default daquela sessão. A interface informa essa
limitação explicitamente.

## Runtime Gateway

O gateway é executado separadamente em `127.0.0.1:11435` por padrão:

- `POST /api/generate` mantém o formato Ollama e injeta o perfil salvo do modelo.
- `POST /v1/chat/completions` oferece compatibilidade OpenAI para clientes como OpenCode.
- `GET /api/tags`, `GET /api/version`, `POST /api/show` e `GET /api/ps` são pass-throughs autenticáveis.

Valores explicitamente salvos pela aplicação têm precedência sobre valores
enviados pelo cliente. Valores em Default permanecem ausentes e deixam o cliente
ou Ollama decidir. Streaming ainda retorna erro explícito até existir um
adaptador de streaming validado.
