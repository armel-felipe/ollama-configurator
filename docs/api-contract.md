# Contrato inicial da API

O contrato HTTP usa prefixo `/api` e é servido apenas no endereço local.

## Fundação

- `GET /api/health` retorna `{ "status": "ok", "version": string }`.
- `GET /api/models/{model_id}/settings` retorna `{ "model": string, "options": object }`.
- `PUT /api/models/{model_id}/settings` salva overrides básicos do modelo.
- `DELETE /api/models/{model_id}/settings/{parameter}` remove um override específico.
- `POST /api/models/{model_id}/apply` reaplica os overrides através da API Ollama.

Parâmetros básicos atuais: `num_ctx`, `temperature`, `num_predict` e
`keep_alive`. O marcador `"default"` remove o override; ele não é convertido
para `0` ou `false`.

Configurações e endpoints adicionais serão adicionados junto às tarefas que os
implementam, sempre com schemas explícitos e erros estruturados.
