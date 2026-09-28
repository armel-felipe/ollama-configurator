# Roadmap de implantação

O roadmap completo está em
`docs/superpowers/plans/2026-09-28-ollama-configurator-implementation.md`.

Os primeiros gates são:

1. Fundação: backend e frontend iniciam.
2. Descoberta: Ollama, hardware e modelos aparecem.
3. Configuração: parâmetros de modelo persistem.
4. MVP 0.1: configurações, resets, diagnóstico, configurações globais do servidor (incluindo KV Cache) e restart funcionam em macOS e Windows.

## Gate atual: validação de inferência

A etapa 7 está funcional para aplicação de perfil e runtime, mas permanece
bloqueada para avanço da etapa 8 até existir um caminho de inferência dentro da
própria aplicação. O motivo é que `think` é um campo por requisição da API; uma
sessão independente iniciada por `ollama run` pode continuar usando o default do
modelo.

Correção planejada:

1. adicionar um painel de teste/chat por modelo;
2. enviar cada prompt usando o perfil salvo, incluindo `think`;
3. separar `thinking` e resposta final;
4. exibir o valor solicitado, o valor retornado e o runtime observado;
5. testar `false`, `true` e níveis declarados pelo modelo;
6. só liberar a etapa 8 depois de validar o fluxo real de inferência.
