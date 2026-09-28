# Roadmap de implantação

O roadmap completo está em
`docs/superpowers/plans/2026-09-28-ollama-configurator-implementation.md`.

Os primeiros gates são:

1. Fundação: backend e frontend iniciam.
2. Descoberta: Ollama, hardware e modelos aparecem.
3. Configuração: parâmetros de modelo persistem.
4. MVP 0.1: configurações, resets, diagnóstico, configurações globais do servidor (incluindo KV Cache) e restart funcionam em macOS e Windows.

## Gate atual: validação de inferência — concluído

A etapa 7A foi concluída. A aplicação agora possui um caminho de inferência
próprio para provar o perfil salvo em uma requisição real. O teste real com
`gemma4:26b-mlx` confirmou `think=false`, ausência de thinking recebido e
contexto efetivo de 16K em `/api/ps` e `ollama ps`.

Correção implantada:

1. adicionar um painel de teste/chat por modelo;
2. enviar cada prompt usando o perfil salvo, incluindo `think`;
3. separar `thinking` e resposta final;
4. exibir o valor solicitado, o valor retornado e o runtime observado;
5. testar `false`, `true` e níveis declarados pelo modelo;
6. liberar a etapa 8 depois da validação do fluxo real de inferência.

A limitação permanece documentada: uma sessão independente iniciada por
`ollama run` não herda o perfil da aplicação, pois `think` é por requisição.
