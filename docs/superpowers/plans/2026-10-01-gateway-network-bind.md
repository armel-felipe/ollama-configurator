# Plano de implementação: bind de rede do Gateway para Tailscale

## Goal

Adicionar ao Ollama Configurator uma configuração persistente para o endereço de
escuta do Runtime Gateway na porta `11435`, com `127.0.0.1` como padrão e
`0.0.0.0` como opção explícita para acesso via LAN/Tailscale. A mudança deverá
ser aplicada somente ao gateway, com estado verificável na UI, sem reiniciar o
aplicativo inteiro e sem deixar processos filhos órfãos.

## Architecture

- A configuração do bind ficará em uma seção própria `gateway` do
  `config.json`, separada das variáveis globais `server`/`OLLAMA_*`.
- Um pequeno serviço de configuração do gateway fará validação, persistência,
  leitura do valor efetivo e cálculo de `pending_restart`.
- `GatewayProcessManager` continuará sendo o dono do processo filho, mas
  passará a aceitar um host efetivo por ciclo de vida e a trocar o bind somente
  depois de encerrar o processo anterior.
- A API manterá as rotas existentes de status/início/parada/reinício e ganhará
  rotas explícitas para ler, salvar e aplicar a configuração do bind.
- A UI exibirá o bloco “Acesso do gateway” junto aos controles do gateway,
  separando: valor editado, valor salvo, valor efetivo, aplicação pendente,
  reinício em andamento e falha de bind.
- O modo `0.0.0.0` continuará sendo um endereço de escuta, não um endereço para
  o cliente usar. A UI deverá deixar explícito que o cliente remoto usa o IP
  Tailscale real da máquina servidora; não haverá descoberta automática.

## Tech Stack

- Backend: Python, FastAPI, Pydantic, `ConfigStore`, `httpx`, `pytest`.
- Frontend: React, TypeScript, Vitest, Testing Library, CSS existente.
- Empacotamento: PyInstaller/frozen backend e os manifests atuais de macOS e
  Windows.
- Verificação: testes backend/frontend, Ruff, build frontend, build frozen e
  smoke test HTTP controlado.

## Spec

[Especificação aprovada](../specs/2026-10-01-gateway-network-bind-design.md)

## Global Constraints

- Preservar a porta `11435`, as rotas Ollama/OpenAI e os controles atuais de
  iniciar, parar, reiniciar e liberar processo externo.
- Preservar `127.0.0.1` como comportamento padrão e compatibilidade com
  configurações antigas sem a seção `gateway`.
- Não alterar a porta original do Ollama (`11434`), firewall, ACLs do Tailscale,
  descoberta de IP ou configuração automática de segurança da rede.
- Não reiniciar a aplicação inteira ao aplicar o bind do gateway.
- Não encerrar processos que não pertençam ao gateway gerenciado sem a ação
  explícita já existente de liberar processo externo.
- Não tratar `0.0.0.0` como endereço de conexão de um cliente remoto.
- Preservar tema claro/escuro e acessibilidade dos controles atuais.
- Não descartar alterações existentes e não alterar arquivos gerados ou assets
  que não sejam necessários para esta etapa.

## Review Focus

- A transição entre host salvo e host efetivo não pode produzir um falso
  “ativo”.
- O caminho de apply/restart deve encerrar o filho anterior antes de tentar o
  novo bind e deve expor erro acionável se o bind falhar.
- O modo wildcard deve funcionar tanto no código-fonte quanto no bundle frozen.
- O estado persistido deve sobreviver à recarga e ao reinício do aplicativo.
- O teste deve cobrir processo externo, restart, ausência de configuração,
  host inválido e ausência de processo órfão.

## Implementation Tasks

### Task 1 — Criar o contrato persistente e o serviço de configuração do gateway

**Files:**

- `backend/persistence/store.py`
- `backend/gateway_settings.py` (novo)
- `tests/unit/test_gateway_settings.py` (novo)
- `tests/unit/test_store.py`

**RED:** adicionar testes que carreguem uma configuração antiga sem `gateway` e
obtenham `127.0.0.1`; aceitem e persistam `0.0.0.0`; rejeitem hosts arbitrários;
calculem `pending_restart` quando o host salvo divergir do efetivo; e mantenham
o arquivo intacto quando houver JSON corrompido.

**Implementação:**

- Definir constantes imutáveis para o host padrão, host de rede permitido,
  porta e opções públicas.
- Implementar um serviço com operações `get(effective_host)`, `update(host,
  effective_host)` e `reset(effective_host)`, usando `ConfigStore` e a seção
  `gateway` sem quebrar `models` ou `server`.
- Persistir apenas valores permitidos, usando escrita atômica já existente.
- Retornar estado serializável contendo `host`, `effective_host`, `port`,
  `pending_restart`, opções e aviso de rede quando aplicável.

**GREEN/Verification:** executar os testes novos e os testes atuais de store;
confirmar que `config.json` antigo continua válido e que salvar/resetar não
remove perfis de modelo nem configurações globais do Ollama.

**Commit:** `feat: persist gateway network bind settings`

### Task 2 — Tornar o ciclo de vida do gateway compatível com host configurável

**Files:**

- `backend/gateway_manager.py`
- `backend/app.py`
- `backend/api/gateway_routes.py`
- `backend/__main__.py` (somente se o contrato frozen precisar de ajuste)
- `tests/unit/test_gateway_manager.py`
- `tests/unit/test_app_gateway_lifecycle.py`

**RED:** adicionar testes que verifiquem comando com `127.0.0.1` e com
`0.0.0.0`; health check de wildcard via loopback; identificação de listener
externo na porta wildcard; restart que termina o processo anterior antes de
criar o próximo; e falha de processo/bind refletida como `error` com detalhe.

**Implementação:**

- Adicionar validação centralizada do host e um método de restart que aceite o
  novo host somente no ciclo controlado de aplicação.
- Manter o host efetivo no status; não alterar esse valor quando apenas a
  configuração for salva.
- Fazer `_health_check` sondar `127.0.0.1` quando o bind for `0.0.0.0`, sem
  mudar o endereço de escuta do processo.
- Ajustar a detecção `lsof` para encontrar listener wildcard de forma
  confiável, sem ampliar a ação de encerramento de processos externos.
- Sincronizar o host persistido antes do autostart do lifespan e garantir que o
  caminho frozen continue usando `--gateway --host ... --port ...`.
- Emitir logs de início, aplicação, parada e erro com host e porta.

**GREEN/Verification:** executar testes unitários e o teste de ciclo de vida;
usar um processo fake para provar que `stop` ocorre antes do novo `start` e que
nenhuma referência ao processo antigo permanece.

**Commit:** `feat: support configurable gateway bind lifecycle`

### Task 3 — Expor leitura, salvamento e aplicação pela API

**Files:**

- `backend/api/gateway_routes.py`
- `backend/api/schemas.py` ou novo módulo de schemas, conforme o padrão já
  usado pelo projeto
- `tests/integration/test_gateway_manager_routes.py`
- `tests/integration/test_gateway_settings_routes.py` (novo)

**RED:** testar:

- `GET /api/gateway/settings` com padrão local;
- atualização válida para `0.0.0.0` retornando `pending_restart=true`;
- host inválido com `422`;
- apply/restart usando o host salvo e retornando status efetivo;
- erro de bind preservando mensagem acionável e não mascarando o status;
- rotas legadas de status, start, stop, restart e release-external.

**Implementação:**

- Adicionar `GET /api/gateway/settings` e `PUT /api/gateway/settings`.
- Adicionar `POST /api/gateway/apply`, que carrega o host persistido, reinicia
  apenas o gateway e devolve estado efetivo.
- Manter `/api/gateway/restart` como reinício do host efetivo atual para
  compatibilidade; o novo botão de aplicação usará `/apply`.
- Traduzir erros de validação para `422` e falhas de lifecycle para `409` com
  mensagem operacional.
- Garantir que o manager usado pela API e pelo lifespan compartilhe a mesma
  configuração e não crie instâncias concorrentes.

**GREEN/Verification:** executar a suíte de integração com `httpx.ASGITransport`
e verificar o JSON completo dos estados pendente, iniciando, ativo e erro.

**Commit:** `feat: expose gateway bind settings api`

### Task 4 — Implementar o fluxo de configuração e estado na UI

**Files:**

- `frontend/src/api/client.ts`
- `frontend/src/features/gateway/GatewayControls.tsx`
- `frontend/src/features/diagnostics/DiagnosticsPage.tsx` (se necessário para
  carregar e publicar o novo estado)
- `frontend/src/styles.css` ou arquivo de estilos efetivamente usado
- `frontend/src/features/gateway/gatewayControls.test.tsx`
- `frontend/src/features/diagnostics/diagnostics.test.tsx`

**RED:** adicionar testes para:

- seletor com as opções local/rede e padrão local;
- aviso explícito ao escolher `0.0.0.0`;
- alteração visualmente pendente sem chamar apply automaticamente;
- botão “Aplicar e reiniciar gateway” desabilitado sem alteração e habilitado
  com alteração salva;
- sequência aplicação → iniciando → ativo com host efetivo;
- erro acionável sem perder o valor selecionado;
- recarga que lê o valor persistido;
- contraste e conteúdo legíveis nos temas claro e escuro.

**Implementação:**

- Adicionar tipos e clientes para settings/apply do gateway.
- Colocar o bloco “Acesso do gateway” dentro da área do gateway, próximo do
  status e dos controles de lifecycle, e não dentro das configurações globais
  do Ollama.
- Separar claramente “salvo”, “pendente” e “efetivo agora”; não reutilizar a
  mensagem genérica de configurações globais.
- Exibir `127.0.0.1:11435` no modo local e, no modo de rede, explicar que o
  serviço escuta em todas as interfaces e que o cliente remoto deve usar o IP
  Tailscale real.
- Associar o botão de apply exclusivamente ao gateway e manter o botão de
  reinício da aplicação separado.
- Atualizar o resumo operacional para distinguir bind pendente de gateway ativo.

**GREEN/Verification:** rodar Vitest e realizar inspeção visual em tema claro e
escuro, incluindo viewport estreito e estados de erro/loading.

**Commit:** `feat: add gateway bind controls to ui`

### Task 5 — Atualizar conexão, documentação e contrato operacional

**Files:**

- `frontend/src/features/connections/ConnectionsPage.tsx`
- `frontend/src/features/connections/connectionCommands.ts`
- `frontend/src/features/connections/connections.test.tsx`
- `frontend/src/features/connections/connectionCommands.test.ts`
- `README.md`
- `docs/api-contract.md`
- `docs/development-setup.md`
- `docs/security.md`
- `docs/roadmap.md`
- `docs/runbooks/ollama-unavailable.md` (se o fluxo de recuperação for
  afetado)

**RED:** testar que o modo local continua gerando os comandos atuais e que o
modo de rede não apresenta `0.0.0.0` como se fosse um endereço remoto utilizável;
o comando deverá instruir o usuário a substituir pelo IP Tailscale da máquina
servidora quando necessário.

**Implementação:**

- Atualizar a área de conexão para refletir bind local versus escuta de rede,
  sem inventar descoberta de IP.
- Documentar a sequência: selecionar `0.0.0.0`, salvar, aplicar/reiniciar o
  gateway, validar `/health` e então apontar o cliente remoto para
  `http://<IP_TAILSCALE>:11435`.
- Documentar que `OLLAMA_HOST` direciona o cliente para o gateway, que a porta
  `11434` continua independente e que a chave de API é recomendada para rede.
- Registrar a etapa no roadmap como implementação concluída somente após QA.

**GREEN/Verification:** rodar testes de comandos/conexões e revisar toda a
documentação para não sugerir `0.0.0.0` como URL de cliente.

**Commit:** `docs: document gateway network access`

### Task 6 — Gauntlet técnico, QA global e validação do bundle

**Files/artefatos:**

- `tests/` conforme ajustes necessários
- `scripts/build_backend.py`
- `docs/testing.md`
- `docs/packaging.md`
- relatório de QA em `docs/qa/` somente se o padrão existente exigir um arquivo

**Implementação/Verification:** executar, sem pular falhas:

1. `uv run pytest -q`;
2. `uv run ruff check backend tests`;
3. `npm test --prefix frontend -- --run`;
4. `npm run build --prefix frontend`;
5. build frozen macOS e smoke test do backend;
6. iniciar bundle com host padrão, consultar `/health` na `11435`, aplicar
   `0.0.0.0` em ambiente controlado, consultar `/health` novamente e parar;
7. verificar via processo/porta que não há filho órfão após stop/restart;
8. validar persistência recarregando a UI e reiniciando o backend;
9. fazer QA manual da UI em claro/escuro, erro de porta ocupada, processo
   externo, rede pendente e gateway ativo;
10. revisar `git diff`, arquivos gerados indevidos, tipagem, lint e documentação.

**Critério de saída:** todos os testes passam, a porta responde nos dois modos,
o estado exibido corresponde ao processo real, a aplicação não deixa processo
órfão e a documentação explica claramente como usar o IP Tailscale.

**Commit:** `test: verify gateway network bind end to end`

## Execution Order

Executar estritamente na ordem 1 → 6. Cada tarefa deve passar pelo ciclo
RED → implementação → GREEN → revisão do diff antes do commit. Se uma etapa
alterar o contrato da seguinte, atualizar primeiro os testes de contrato e
registrar a decisão no próprio commit da etapa.
