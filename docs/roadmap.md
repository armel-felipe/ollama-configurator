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

## Runtime Gateway — 7B concluído

O gateway é a porta de entrada compatível com Ollama e OpenAI para clientes como
OpenCode. Por padrão ele fica somente em `127.0.0.1:11435`; para uso via
Tailscale, pode escutar explicitamente no IP da interface Tailscale e exige uma
chave de acesso.

QA real concluído: `100.87.71.48:11435` respondeu pelo Tailscale, uma chamada
OpenAI-compatible chegou ao Gemma4 e o perfil salvo continuou prevalecendo.

## Streaming do Runtime Gateway — 7C concluído

O gateway agora adapta o fluxo incremental do Ollama para NDJSON e SSE
compatível com OpenCode, mantendo o perfil salvo — inclusive `think=false` — em
cada requisição. O Gemma4 foi validado em streaming real com múltiplos chunks e
marcador `[DONE]`.

Correção adicional: erros ocorridos durante o streaming OpenAI-compatible agora
usam um envelope `error` com `message` e `type`, em vez de uma string simples.
Isso evita que o OpenCode rejeite a resposta por ausência de `choices` ou por
tipo inválido do campo `error`.

Também foi adicionada a normalização de mensagens OpenAI que chegam com
`content` como partes de texto. O Ollama nativo exige uma string; a gateway
agora converte essas partes antes de encaminhar, mantendo compatibilidade com
o OpenCode.

## Compatibilidade nativa de clientes Ollama — 7D concluído

Adicionado `/api/chat` à gateway para que `OLLAMA_HOST` possa
apontar para `11435` e clientes como `ollama run` também passem pelo perfil
salvo da aplicação.

QA de contrato concluído: `/api/chat` normal e streaming NDJSON usam o perfil
salvo e preservam `think=false`.

## Controle visual da gateway — 7E concluído

A aplicação agora inicia, para, reinicia e monitora a gateway na porta `11435`,
sem exigir comando manual no terminal. O padrão continua sendo bind local em
`127.0.0.1`; a configuração Tailscale permanece explícita.

### Observabilidade contínua — concluído

O indicador da UI agora exibe `Ativo — respondendo` e continua consultando o
estado da gateway enquanto ela está ativa. Se o processo ou o endpoint deixar de
responder, o status deixa de permanecer silenciosamente como ativo; a tela
passa a refletir a nova condição e os controles de recuperação ficam visíveis.

### Aplicação verificável do contexto — em validação

O botão **Aplicar no Ollama** agora consulta o runtime depois do recarregamento
e compara o `num_ctx` solicitado com o `context_length` retornado por `/api/ps`.
Se o scheduler mantiver a instância anterior durante a primeira tentativa, a
aplicação faz uma segunda recarga. Se ainda houver divergência, o resultado é
marcado como não aplicado e a UI mostra os valores solicitado e efetivo; ela
não apresenta mais uma confirmação falsa.

O critério de conclusão desta etapa é alterar 16K, 32K e 64K em um modelo
carregado, confirmar cada valor no `ollama ps` e repetir a validação por uma
chamada externa à gateway.
