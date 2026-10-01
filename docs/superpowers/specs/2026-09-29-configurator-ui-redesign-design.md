# Ollama Configurator — redesign de interface

## Objetivo

Transformar a interface atual, que apresenta informações técnicas sem hierarquia
visual suficiente, em uma aplicação local limpa, profissional e elegante para
configurar e acompanhar runtimes Ollama.

O usuário deve conseguir responder rapidamente a três perguntas:

1. Qual modelo estou configurando?
2. O que está salvo e o que está efetivamente rodando?
3. O que preciso fazer para aplicar uma alteração?

## Direção visual

- Produto desktop de operação técnica, com acabamento de ferramenta profissional.
- Tema claro como padrão inicial.
- Tema escuro alternável pelo topo da aplicação e persistido localmente.
- Paleta neutra, com cor de destaque usada apenas para ações e estados positivos.
- Tipografia com hierarquia clara, espaçamento generoso e poucos elementos por tela.
- Controles com aparência inequívoca: botões primários, toggles liga/desliga,
  barra segmentada para presets e campos personalizados claramente distintos.
- Evitar aparência de dashboard genérico, excesso de cards, texto técnico sem
  contexto e estados representados somente por cor.

## Arquitetura de informação

### Navegação principal

Uma navegação lateral compacta contém:

- Modelos — tarefa principal;
- Servidor — configurações globais e gateway;
- Diagnóstico — descoberta, hardware, logs e validações avançadas.

O estado da gateway permanece resumido na navegação, por exemplo “Ativo” ou
“Parado”, sem competir com o editor de modelo.

### Editor de perfil

Ao selecionar um modelo, a área principal apresenta um único perfil editável:

- cabeçalho com nome do modelo, runner, estado carregado e estado do perfil;
- Context Window com presets 16K, 32K, 64K, 128K e 256K;
- entrada livre separada para valores personalizados;
- Reasoning / Thinking com toggle ou seletor conforme os valores declarados
  pelo modelo;
- parâmetros secundários como temperature, max output e keep alive;
- ação primária “Salvar e aplicar”.

Salvar e aplicar deve ser uma ação visualmente dominante. Alterações pendentes,
salvas e aplicadas devem ser estados diferentes e explícitos.

### Runtime efetivo

O runtime é uma confirmação compacta do perfil, não outro editor concorrente.
Ele deve mostrar lado a lado:

- solicitado;
- efetivo;
- estado da aplicação;
- processador/runner;
- thinking efetivo quando disponível.

Uma divergência como “solicitado 64K · efetivo 128K” deve ser tratada como
alerta de aplicação, nunca como confirmação de sucesso.

### Inferência

O teste de inferência permanece no produto como ferramenta de validação técnica,
mas sai do fluxo principal de configuração. Ele ficará em Diagnóstico avançado,
com explicação curta de que valida o perfil salvo pela aplicação e não controla
uma sessão independente iniciada por `ollama run`.

## Temas

- Primeira abertura: tema claro.
- Alternância: controle visível no topo, com ícone e texto acessível indicando o
  tema de destino.
- Persistência: preferência salva no armazenamento local da aplicação.
- Os dois temas devem preservar contraste, hierarquia, estados e affordances;
  tema escuro não será apenas uma inversão automática de cores.
- O layout não deve depender de cor para transmitir “aplicado”, “pendente” ou
  “erro”; ícone, texto e estrutura também participam do estado.

## Estados essenciais

- Ollama indisponível: estado de diagnóstico acionável, sem quebrar o layout.
- Nenhum modelo instalado: orientação clara para instalar ou atualizar a lista.
- Modelo selecionado, perfil sem alterações: “Aplicado”.
- Alteração local: “Alterações pendentes”; aplicar fica habilitado após salvar.
- Aplicação em andamento: botão bloqueado com progresso textual.
- Aplicação confirmada: solicitado e efetivo coincidem.
- Aplicação divergente: alerta persistente até nova aplicação ou correção.
- Gateway: parado, iniciando, ativo — respondendo, externo ou erro.

## Responsividade e acessibilidade

- Desktop macOS e Windows como prioridade.
- Em larguras menores, a navegação lateral pode virar uma barra superior ou
  gaveta, sem esconder a ação primária.
- Todos os controles têm nome acessível, foco visível e operação por teclado.
- Toggles devem expor estado ligado/desligado semanticamente.
- Mensagens de aplicação usam regiões de status e alertas apropriadas.

## Escopo da primeira implementação visual

1. Criar shell visual com navegação lateral, cabeçalho e alternância de tema.
2. Reorganizar a tela de modelos e o editor de perfil.
3. Reorganizar controles de parâmetros e estados de salvar/aplicar.
4. Reduzir o runtime para um bloco de confirmação objetivo.
5. Mover o teste de inferência para Diagnóstico avançado.
6. Adicionar testes de tema, navegação, estados e acessibilidade básica.
7. Executar QA visual em tema claro e escuro, desktop e viewport estreito.

## Fora do escopo desta rodada

- Alterar contratos do Ollama ou a lógica de aplicação do runtime.
- Implementar ainda as configurações globais da etapa 8.
- Criar instaladores macOS/Windows.
- Criar perfis múltiplos ou recomendações automáticas.

