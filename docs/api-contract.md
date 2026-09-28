# Contrato inicial da API

O contrato HTTP usa prefixo `/api` e é servido apenas no endereço local.

## Fundação

- `GET /api/health` retorna `{ "status": "ok", "version": string }`.
- `GET /api/models/{model_id}/settings` retorna overrides, defaults nativos e a especificação `thinking` declarada pelo modelo em `/api/show`.
- `PUT /api/models/{model_id}/settings` salva overrides básicos do modelo.
- `DELETE /api/models/{model_id}/settings/{parameter}` remove um override específico.
- `POST /api/models/{model_id}/apply` descarrega e recarrega o runner com o perfil completo e retorna o runtime observado.
- `GET /api/models/{model_id}/runtime` consulta o modelo carregado em `/api/ps` e retorna contexto, processador e perfil aplicado.

Parâmetros básicos atuais: `num_ctx`, `temperature`, `num_predict` e
`keep_alive`. Thinking é um controle adicional validado contra os valores
declarados pelo próprio modelo. O marcador `"default"` remove o override; ele
não é convertido para `0` ou `false`.

Configurações e endpoints adicionais serão adicionados junto às tarefas que os
implementam, sempre com schemas explícitos e erros estruturados.
