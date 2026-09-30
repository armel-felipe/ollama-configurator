# Redesign: shell com rolagem independente e ícones de marca

**Data:** 2026-09-30  
**Status:** Aprovado para planejamento técnico  
**Escopo:** moldura principal e tela de conexões

## Objetivo

Manter a marca, a navegação e o estado do gateway visíveis enquanto o usuário rola uma área longa de configurações, além de substituir os ícones genéricos dos cards de conexão por marcas oficiais locais.

## Decisões aprovadas

### Moldura

- No desktop, a aplicação usa uma moldura de duas colunas com altura da janela.
- A coluna esquerda contém o logo oficial do Ollama, “Ollama Configurator”, navegação e status do gateway.
- O conteúdo da direita possui rolagem própria.
- A navegação esquerda pode rolar internamente sem mover o conteúdo da direita.
- Em viewport pequena, volta a uma coluna única com navegação horizontal no topo e sem rolagem presa.

### Ícones

- Usar assets oficiais locais para Ollama, Claude Code, Codex CLI, OpenClaw, OpenCode, Hermes Agent, Hermes Desktop, Droid, Pi, Cline, Copilot CLI, Oh My Pi, DeepSeek Harness, Poolside, Qwen Code e Terminal.
- Não usar hotlink em runtime.
- Registrar fonte e licença/termos de uso na documentação.
- Se uma marca não tiver asset oficial reutilizável ou licença verificável, usar fallback neutro e registrar a decisão.
- Os nomes textuais permanecem visíveis; os ícones são decorativos e acessíveis via `aria-hidden` quando apropriado.

### Fluxos preservados

- Clicar em um card continua selecionando o cliente e copiando automaticamente o comando.
- O estado “Copiado”, o status do gateway e os temas claro/escuro permanecem funcionando.
- Não reintroduzir uma área redundante de comando.

## Estrutura

```text
app-shell (altura da janela)
├── sidebar
│   ├── brand
│   ├── nav-scroll
│   └── gateway-status
└── content-scroll
    └── seção ativa
```

No desktop, `body` não deve ser a rolagem principal: a moldura controla as áreas `overflow`. No mobile, preservar uma única leitura vertical natural.

## Verificação

1. A marca e a navegação permanecem visíveis ao rolar Modelos, Servidor, Diagnóstico ou Conexões.
2. A navegação esquerda rola independentemente quando necessário.
3. Não há rolagem horizontal acidental ou conteúdo inacessível em mobile.
4. Os 15 cards exibem assets locais e identificáveis ou fallback documentado.
5. Ícones têm contraste adequado em tema claro e escuro.
6. Seleção, cópia e acessibilidade continuam funcionando sem dependência remota.
7. Typecheck, testes, build, inspeção visual desktop/mobile e detector visual do Impeccable passam.

## Fora de escopo

Alterações no gateway, persistência, formulários de parâmetros, comandos Ollama, novos clientes ou instalador desktop.

