# Logs operacionais e recuperação de gateway externo

## Objetivo

Dar visibilidade operacional ao Configurator e oferecer uma recuperação segura
quando a porta `11435` estiver ocupada por um processo externo.

## Escopo aprovado

- Registrar eventos técnicos do Configurator, Gateway e Ollama.
- Exibir os eventos em tempo real na UI por SSE.
- Não registrar nem exibir o conteúdo do raciocínio interno do modelo.
- Identificar processo externo que ocupa a porta `11435`.
- Permitir encerrá-lo somente após confirmação explícita.

## Arquitetura

O backend terá um buffer circular em memória para eventos recentes e um
publicador SSE. Cada evento terá horário, serviço, nível, mensagem e metadados
seguros. O gateway publicará eventos de ciclo de vida e requisição; a aplicação
publicará eventos de configuração, reinício e erro.

A UI terá um painel de logs com filtros por serviço, pausa da rolagem, limpeza
visual e indicação de conexão ao fluxo ao vivo. O histórico será volátil e não
será persistido em disco nesta etapa.

O `GatewayProcessManager` enriquecerá o estado externo com PID e identificação
quando disponível. A ação de encerramento validará que o PID ainda ocupa a
porta configurada antes de enviar término; falhas serão reportadas sem matar
processos arbitrários.

## Critérios de aceite

1. Um evento gerado pelo backend aparece no fluxo SSE e na UI.
2. Filtros não misturam eventos de serviços diferentes.
3. A UI informa quando a conexão ao fluxo está ativa ou interrompida.
4. Um listener externo é mostrado com PID/identificação quando disponível.
5. O encerramento exige confirmação e, após concluir, a UI permite iniciar o
   gateway gerenciado.
6. Testes backend, frontend, lint, typecheck e build permanecem verdes.
