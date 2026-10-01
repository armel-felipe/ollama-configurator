# Gateway em rede local/Tailscale — especificação

**Data:** 2026-10-01  
**Status:** aprovado para especificação; implementação pendente de revisão deste documento

## Objetivo

Permitir que o Runtime Gateway do Ollama Configurator seja acessado por clientes
em outra máquina da rede Tailscale, mantendo o comportamento local e seguro como
padrão.

## Escopo

O configurador passará a oferecer duas opções para o endereço de escuta do
gateway na porta `11435`:

- `127.0.0.1`: acesso somente na máquina que executa o configurador. É o padrão.
- `0.0.0.0`: escuta em todas as interfaces disponíveis, incluindo a interface
  Tailscale, permitindo acesso por `http://<ip-tailscale>:11435`.

Esta configuração controla o gateway do configurador, não o servidor Ollama
original da porta `11434`.

## Experiência na UI

Na área de configuração do servidor/gateway haverá um bloco “Acesso do gateway”
com um seletor de endereço e a porta visível (`11435`).

Ao selecionar `0.0.0.0`, a UI exibirá um aviso explícito de exposição de rede:

> O gateway ficará acessível pelas interfaces de rede desta máquina. Use apenas
> em uma rede confiável e considere configurar uma chave de API.

Alterar o seletor deixará o estado como “alteração não aplicada”. O usuário
deverá clicar em “Aplicar e reiniciar gateway”. A UI mostrará:

- alteração pendente;
- gateway reiniciando;
- gateway ativo, com endereço efetivo e porta;
- erro acionável caso a porta esteja ocupada ou o bind falhe.

Não haverá reinício do aplicativo inteiro para essa mudança.

## Persistência e ciclo de vida

O endereço escolhido será salvo na configuração persistente do configurador e
será reutilizado quando a aplicação for reiniciada. O valor padrão será
`127.0.0.1` quando não houver configuração salva.

O `GatewayProcessManager` deverá receber o host configurado ao iniciar ou
reiniciar o processo. O processo filho deverá ser encerrado antes de iniciar o
novo bind, evitando processos órfãos e conflitos na porta `11435`.

O status do gateway deverá distinguir:

- parado;
- iniciando;
- ativo e respondendo;
- processo externo ocupando a porta;
- erro de inicialização.

## Segurança

O gateway continuará local por padrão. A escolha de `0.0.0.0` será explícita e
acompanhada de aviso. A configuração de chave de API existente continuará sendo
respeitada pelo gateway; a UI deverá indicar que ela é recomendada quando o
bind de rede estiver ativo.

O recurso não abrirá portas no roteador nem configurará o Tailscale. O usuário
continua responsável pelo firewall do sistema, pelas ACLs do tailnet e pelo IP
usado pelo cliente remoto.

## Arquitetura e contrato

- O catálogo de configurações do servidor incluirá o host do gateway como uma
  configuração própria, separada das variáveis globais do Ollama.
- As rotas existentes de status, iniciar, parar e reiniciar serão preservadas.
- A rota de atualização retornará o host efetivo, o estado pendente e o próximo
  estado esperado.
- O gateway continuará compatível com clientes Ollama/OpenAI que apontem para a
  porta `11435`.
- O endereço anunciado para clientes remotos será derivado do host informado
  pelo usuário; o gateway não tentará adivinhar um IP Tailscale.

## Testes e critérios de aceitação

### Backend

- valor ausente usa `127.0.0.1`;
- `0.0.0.0` é aceito e persistido;
- hosts inválidos são rejeitados;
- alteração marca reinício pendente;
- reinício usa o host escolhido;
- processo filho anterior é encerrado antes do novo;
- falha de bind retorna estado e mensagem acionáveis;
- status identifica corretamente gateway gerenciado e processo externo.

### Frontend

- seletor mostra as duas opções e o padrão local;
- seleção de rede exibe o aviso de exposição;
- alterações não são apresentadas como aplicadas antes da ação;
- botão de aplicar/reiniciar fica claramente associado ao gateway;
- status muda corretamente entre pendente, iniciando, ativo e erro;
- recarga da página preserva a configuração salva;
- tema claro e escuro mantêm contraste e legibilidade.

### Empacotamento e QA

- testes backend e frontend completos;
- lint e build de produção;
- bundle macOS inicia com o host padrão;
- bundle macOS inicia com `0.0.0.0` em ambiente controlado;
- endpoint `/health` responde na porta `11435`;
- nenhum processo filho permanece após parar/reiniciar o gateway;
- documentação de uso via Tailscale atualizada.

## Fora do escopo

- criação automática de regras de firewall;
- configuração automática do Tailscale ou de ACLs;
- descoberta automática do IP Tailscale;
- exposição pública pela internet;
- alteração do servidor Ollama original na porta `11434`.
