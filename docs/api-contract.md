# Contrato inicial da API

O contrato HTTP usa prefixo `/api` e é servido apenas no endereço local.

## Fundação

- `GET /api/health` retorna `{ "status": "ok", "version": string }`.

Configurações e endpoints adicionais serão adicionados junto às tarefas que os
implementam, sempre com schemas explícitos e erros estruturados.
