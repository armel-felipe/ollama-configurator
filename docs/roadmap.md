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

Correção adicional de compatibilidade: o último chunk SSE agora repassa
`prompt_tokens`, `completion_tokens` e `total_tokens` derivados das métricas do
Ollama. Isso permite que clientes como OpenCode atualizem seus indicadores de
tokens/s ao usar a porta `11435`, como já ocorria diretamente na `11434`.

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

## Etapa 8 — Configurações globais do servidor: concluída em macOS

A aplicação agora exibe as configurações globais antes da seleção de modelo,
com valores efetivos, padrões explícitos e indicação de reinício pendente.
Foram incluídos KV cache (`f16`, `q8_0`, `q4_0`), Flash Attention, contexto
global, keep-alive, paralelismo, limite de modelos carregados, fila, overhead
de GPU e scheduler.

No macOS, os overrides persistem em um LaunchAgent gerenciado por usuário e
são reaplicados no login. O botão de reinício encerra e reabre o Ollama e
reaplica os perfis de modelo salvos pelo coordenador único de reinício. Reset
remove os overrides sem apagar modelos ou pesos.

QA da etapa: 58 testes backend, 31 testes frontend, typecheck, build,
Ruff e mypy aprovados. A validação de logout/login/reboot físico depende de
execução no macOS instalado; o contrato do LaunchAgent e o fluxo de reexecução
foram cobertos por testes isolados.

### Gate de execução do MVP — corrigido

O desenvolvimento agora possui um launcher único (`scripts/dev.py`) que inicia
backend e frontend juntos. Quando o backend local não responde, a UI informa a
causa e a porta `8787`, em vez de exibir apenas uma falha genérica de leitura.
Quando necessário, o painel também oferece **Reiniciar aplicação**, que solicita
ao supervisor a reinicialização coordenada dos dois processos e recarrega a UI.

### Correção registrada — reinício do Ollama no macOS

O fluxo de aplicação das configurações globais agora trata versões do aplicativo
Ollama que rejeitam o encerramento via AppleScript. Nessa situação, o adaptador
usa um fallback controlado por processo, reabre o aplicativo pelo bundle
`/Applications/Ollama.app` quando necessário e mantém falhas de permissão
explícitas para diagnóstico. Após a reabertura, o coordenador aguarda a
disponibilidade do Ollama e repete a reaplicação dos perfis para evitar corrida
de inicialização. O fluxo foi coberto por testes unitários e validado na UI.

## Observabilidade e recuperação do gateway — implementado

O Configurator agora oferece um painel de logs operacionais em tempo real, com
eventos do Configurator, Gateway e Ollama, filtros por serviço, limpeza da
visualização e indicador explícito de conexão ao fluxo SSE. Os eventos registram
estado, perfil aplicado, porta, modelo e parâmetros efetivos; o conteúdo interno
do raciocínio do modelo não é capturado.

Quando a porta `11435` já está ocupada por um processo externo, a UI identifica
o PID e o nome do processo, explica que a gateway gerenciada não está controlando
esse runtime e oferece **Liberar porta** com confirmação explícita. A ação só
envia `SIGTERM` ao PID identificado pela própria porta; não encerra processos
por nome nem tenta liberar uma porta sem identificação.

QA da implementação: endpoints `/api/logs` e `/api/logs/stream` verificados no
launcher real; gateway iniciada pela UI/API e confirmada como respondendo; painel
validado no navegador com status **Ao vivo** e evento de inicialização visível.

### Próxima correção de UX registrada — ações duplicadas

Ainda está pendente consolidar as ações de ciclo de vida na interface: remover a
duplicidade entre **Iniciar gateway** e **Iniciar servidor**, renomear
**Reiniciar aplicação** para deixar claro que reinicia o Configurator e separar
visualmente as ações de salvar, aplicar e restaurar. Essa correção fica registrada
como a próxima passada de UX, sem alterar o escopo dos logs operacionais.

## Correção de estabilidade do editor de modelo — implementado

O editor de modelo deixou de recarregar o perfil quando o componente pai apenas
atualiza seu estado operacional. As callbacks de carregamento agora são mantidas
atualizadas sem participar do ciclo de recarga; a leitura só acontece ao abrir
outro modelo ou ao solicitar uma nova tentativa. Isso elimina as piscadas e
impede que valores editados sejam sobrescritos, inclusive quando a gateway está
parada.

QA: teste regressivo de identidade das callbacks, 45 testes frontend, 66 testes
backend, typecheck, build, Ruff e mypy aprovados; seleção de modelo e edição de
32K validadas no navegador com a gateway parada.

## Correção de ciclo de vida do launcher — implementado

O launcher agora inicia backend e frontend em grupos de processos próprios e
encerra o grupo inteiro durante parada, reinício ou sinal do terminal. O
supervisor também registra explicitamente a intenção de desligamento; receber
`SIGTERM` não deixa mais o supervisor vivo depois de matar apenas os wrappers
`uv`/`npm`. Isso evita processos órfãos, portas ocupadas silenciosamente e a
perda da UI após **Reiniciar aplicação**.

QA: teste unitário do grupo de processos, reinício real via
`/api/application/restart` com UI/API retornando `200` e apenas uma cadeia de
processos ativa, além de encerramento real confirmado sem processos ou portas
órfãos.

## Conexão com clientes Ollama — implementado

A aplicação agora possui a aba **Conectar**, inspirada na tela de aplicativos
do Ollama, com quinze cards funcionais: Claude Code, Codex, OpenClaw, OpenCode,
Hermes Agent, Hermes Desktop, Droid, Pi, Cline, Copilot CLI, Oh My Pi,
DeepSeek Harness, Poolside, Qwen Code e Terminal.

Cada card gera um comando pronto para copiar, usando o gateway configurado em
`11435`, o modelo selecionado e a sintaxe correta para POSIX ou PowerShell.
Clientes usam `ollama launch <app> --model <modelo>`; o card Terminal usa
`ollama run <modelo> --verbose`. A variável POSIX é emitida como `export
OLLAMA_HOST=...`, evitando o erro do comando apenas com atribuição local em
zsh. A tela não tenta abrir um terminal nativo e informa quando o gateway está
parado.

QA: 18 arquivos e 52 testes frontend aprovados, 68 testes backend aprovados,
typecheck e build de produção aprovados, inspeção visual automatizada executada
e a chamada real `ollama run` com `OLLAMA_HOST` exportado validada contra a
gateway em `11435`. O detector visual apontou somente o uso existente da fonte
Inter como observação de estilo, sem falha funcional.

### Diagnóstico adicional do `400 Bad Request` no terminal

A captura posterior mostrou `400` mesmo com `export OLLAMA_HOST`. A
investigação separou o problema de shell do estado do runtime: a gateway ativa
respondeu `200` para `/api/generate` em streaming e sem streaming, e o comando
exato com duas linhas — `export` seguido de `ollama run` — terminou com código
`0`, incluindo métricas `--verbose`. O erro da captura não foi reproduzido no
processo atual; se voltar a ocorrer, o primeiro diagnóstico deve ser o status
da gateway em `11435` e a existência de um processo antigo/orfão, antes de
alterar o comando.

### Correção de compatibilidade do `ollama run` — implementado

O cliente de terminal também faz uma chamada preliminar a `/api/show` antes de
abrir o streaming. A versão do cliente usada no macOS envia o identificador do
modelo no campo `name`; a gateway aceitava somente `model` e devolvia `400`.
O endpoint agora aceita os dois formatos e encaminha o mesmo identificador ao
Ollama upstream.

QA da correção: teste de regressão reproduzindo `name` passou; `/api/show` real
na porta `11435` passou com `200`; o comando separado em duas linhas
(`export OLLAMA_HOST=...` e `ollama run ... --verbose`) respondeu e exibiu as
métricas. A suíte backend passou com 70 testes. A suíte frontend possui 52
testes reais aprovados, mas o comando amplo ainda tenta interpretar 18 arquivos
AppleDouble `._*.test.*` como código; esses arquivos de metadados binários devem
ser excluídos do escaneamento de testes em uma limpeza posterior.

## Correção de disponibilidade para clientes externos — implementado

Foi identificada a causa do erro de conexão no Terminal e no OpenCode: o
launcher iniciava o backend e o frontend, mas deixava a gateway `11435` parada
até que alguém acionasse uma ação separada na UI. A aplicação agora inicia a
gateway automaticamente no ciclo de vida do backend e a encerra junto com ele.
Se a porta estiver ocupada por outro processo, a aplicação não assume sua
posse; mantém o estado como externo para recuperação explícita.

QA pós-correção: reinício real do supervisor, gateway iniciada automaticamente
com PID gerenciado, endpoint OpenCode-compatible em `/v1/chat/completions`
respondendo `200`, `ollama run` pela porta `11435` terminando com código `0` e
métricas `--verbose`, gateway permanecendo ativa após os dois fluxos; 69 testes
backend aprovados.

## UX da aba Conectar — implementado

Os cards de clientes agora são a ação principal: ao clicar, o comando completo
é copiado diretamente para a área de transferência usando o modelo, shell e
host selecionados. O painel grande e redundante de pré-visualização foi
removido; o feedback permanece no próprio card e em uma região acessível de
status. O comportamento funciona para POSIX e PowerShell.

Os cards passaram a usar ícones SVG locais, consistentes entre tema claro e
escuro, e o cabeçalho recebeu um símbolo Ollama em SVG com cores derivadas do
tema. A referência de integração foi a documentação oficial do Ollama Launch;
os assets ficam locais para a UI continuar funcionando sem depender de rede.

QA: 18 arquivos e 52 testes frontend aprovados, typecheck e build aprovados,
verificação visual no navegador executada em tema claro e detector visual
executado. O detector manteve somente o aviso preexistente sobre a fonte Inter.
