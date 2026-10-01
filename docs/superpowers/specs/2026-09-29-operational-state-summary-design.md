# Resumo operacional da aplicação — opção B

## Objetivo

Tornar imediatamente compreensível se a aplicação, o Ollama, o gateway e as
configurações estão funcionando, sem tirar as configurações do centro da tela.
O usuário deve saber o estado atual e a próxima ação necessária sem interpretar
mensagens técnicas contraditórias.

## Direção escolhida

Manter a tela de configurações como fluxo principal e adicionar um resumo
compacto no topo da área de trabalho. O resumo não será uma nova página nem
uma segunda central de comandos: ele será uma leitura operacional do estado
atual, com no máximo uma ação principal contextual.

## Modelo de estado exibido

O resumo terá quatro indicadores independentes:

1. **Aplicação local** — ativa ou indisponível.
2. **Gateway 11435** — ativo, parado, iniciando, processo externo ou erro.
3. **Configuração global** — salva, alterações não salvas ou aplicação pendente.
4. **Runtime** — não verificado, aplicado ou divergente do solicitado.

Cada indicador terá uma cor, um rótulo textual e uma explicação curta. A cor
nunca será a única informação do estado.

## Ação principal contextual

O resumo apresentará uma ação principal somente quando houver uma transição
clara a executar:

- gateway parado: **Iniciar gateway**;
- alterações locais não salvas: **Salvar configurações**;
- alterações salvas aguardando aplicação: **Aplicar no Ollama**;
- runtime divergente: **Reaplicar perfil**;
- erro recuperável: **Tentar novamente**.

Quando não houver ação pendente, o resumo exibirá apenas “Tudo aplicado” ou
“Aguardando uma execução para confirmar o runtime”.

## Regras de linguagem

- “Salvo” significa persistido pela aplicação, não aplicado no processo.
- “Aplicado” significa que a operação de reinício/reaplicação terminou.
- “Confirmado no runtime” significa que uma leitura posterior verificou o
  valor efetivo.
- “Processo externo” indica que a porta está ocupada por outro processo e que
  a aplicação não poderá controlá-lo.
- Mensagens de erro devem explicar a camada afetada e a ação recomendada.

## Organização visual

- O resumo fica abaixo do cabeçalho da página e antes das configurações.
- Os cartões de configuração continuam sendo a área principal.
- O botão permanente “Reiniciar aplicação” permanece separado da ação de
  aplicar alterações no Ollama.
- O banner de pendência deixa de competir com uma mensagem genérica de “perfil
  salvo”; a ação principal do resumo e o banner devem refletir o mesmo estado.
- A navegação do workspace continua levando às seções da mesma página.

## Comportamento e dados

O resumo deve derivar seu estado das mesmas fontes já usadas pelas telas:

- diagnóstico da aplicação e do Ollama;
- status da gateway;
- configurações globais e `pending_restart`;
- runtime do modelo selecionado, quando houver um modelo selecionado.

Não deve criar uma segunda fonte de verdade nem alterar configurações por si
mesmo. A ação do resumo deve chamar o mesmo handler da tela correspondente.

## Verificação

- Testar cada combinação de estado e ação principal com testes de componente.
- Testar a transição não salvo → salvo → pendente → aplicado.
- Testar gateway externo sem oferecer botão de parada indevido.
- Testar erro de carregamento com mensagem acionável.
- Verificar claro/escuro, viewport estreito e leitura por acessibilidade.
- Fazer QA manual no navegador e confirmar ausência de erros no console.
