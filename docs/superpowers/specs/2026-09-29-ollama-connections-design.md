# Tela de conexões Ollama — especificação de design

## Objetivo

Criar uma aba **Conectar** no Ollama Configurator, seguindo a referência visual fornecida pelo usuário: uma grade de clientes Ollama com identificação clara de cada integração. Todos os cards devem gerar um comando funcional para o terminal, apontando para o gateway gerenciado na porta `11435` e usando o modelo atualmente selecionado.

## Escopo aprovado

Os quinze cards são funcionais e usam os comandos fornecidos pelo usuário:

| Cliente | Subcomando |
| --- | --- |
| Claude Code | `claude` |
| Codex | `codex` |
| OpenClaw | `openclaw` |
| OpenCode | `opencode` |
| Hermes Agent | `hermes` |
| Hermes Desktop | `hermes-desktop` |
| Droid | `droid` |
| Pi | `pi` |
| Cline | `cline` |
| Copilot CLI | `copilot` |
| Oh My Pi | `omp` |
| DeepSeek Harness | `dsh` |
| Poolside | `pool` |
| Qwen Code | `qwen` |
| Terminal | `run` |

Para os quatorze clientes de integração, o segundo comando é:

```text
ollama launch <subcomando> --model <modelo>
```

Para Terminal, o segundo comando é:

```text
ollama run <modelo> --verbose
```

## Comandos por shell

macOS/Linux:

```bash
export OLLAMA_HOST=http://127.0.0.1:11435
<comando Ollama>
```

Windows PowerShell:

```powershell
$env:OLLAMA_HOST="http://127.0.0.1:11435"
<comando Ollama>
```

O comando é sempre composto por duas linhas. A tela não deve juntar a definição de `OLLAMA_HOST` e a execução do Ollama na mesma linha.

## Estrutura da tela

- A navegação existente recebe a seção **Conectar**.
- A seção apresenta título, descrição curta e o host efetivo do gateway.
- Os cards seguem a composição da referência: duas colunas em desktop, uma coluna em viewport estreita, ícone consistente, nome e descrição objetiva.
- O card selecionado recebe estado visual destacado e abre um painel de comando abaixo da grade.
- O painel exibe o cliente, o modelo selecionado, o shell, o host e o comando completo em bloco de código.
- A ação principal é **Copiar comando**. Após copiar, o feedback é temporário e específico: “Comando copiado”.
- Se não houver modelo selecionado, a tela explica que é necessário selecionar um modelo na aba Modelos antes de gerar o comando.
- Se o gateway não estiver ativo, o painel mostra o comando, mas exibe um aviso operacional claro: “Gateway parado — inicie o gateway antes de executar”. A tela não tenta iniciar processos automaticamente.

## Estado e comportamento

- O modelo escolhido é compartilhado com a seleção já existente na aba Modelos.
- Trocar o modelo atualiza o comando sem recarregar a página.
- Trocar macOS/Linux por Windows PowerShell atualiza somente a linha de ambiente; o comando Ollama permanece equivalente.
- O host vem do status real do gateway quando disponível; o fallback documentado é `http://127.0.0.1:11435`.
- O status do gateway é informativo e não bloqueia copiar o comando.
- A seleção do card, shell e feedback de cópia são estados locais da tela.
- Não haverá tentativa de abrir uma janela nativa do Terminal nesta etapa.

## Acessibilidade e responsividade

- Cards são botões com nome acessível e estado `aria-pressed`.
- A área de comando usa texto selecionável, contraste suficiente e quebra horizontal segura.
- O botão de copiar mantém foco visível e feedback anunciado por `aria-live`.
- A grade passa de duas colunas para uma sem perder a ordem dos clientes.
- O tema claro continua padrão; o tema escuro existente deve cobrir a nova tela.

## Critérios de aceitação

1. Os quinze cards aparecem na aba Conectar.
2. Cada card gera o subcomando correto da tabela.
3. O modelo selecionado é interpolado no comando.
4. O host `11435` aparece na primeira linha.
5. Terminal termina com `--verbose`.
6. macOS/Linux usa `export`; Windows PowerShell usa `$env:OLLAMA_HOST=...`.
7. Copiar comando coloca as duas linhas completas na área de transferência.
8. Trocar modelo, shell e gateway atualiza o resultado sem piscar nem perder seleção.
9. Gateway parado é explicado com uma ação de recuperação, sem erro genérico.
10. Os testes unitários, typecheck, build e QA visual desktop/mobile passam.
