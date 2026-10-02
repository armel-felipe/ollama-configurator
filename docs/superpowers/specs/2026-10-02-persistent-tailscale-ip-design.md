# IP Tailscale persistente para conexões — especificação

## Objetivo

Substituir o marcador manual `<IP_TAILSCALE>` da tela **Conectar** por um
endereço IP informado pelo usuário e persistido pela aplicação. O endereço
salvo deve alimentar os comandos de conexão para macOS/Linux e Windows sem
alterar o comportamento local seguro do gateway.

## Escopo aprovado

- A tela **Conectar** exibe o campo **IP Tailscale da máquina servidora** quando
  o gateway está efetivamente vinculado a `0.0.0.0`.
- O usuário informa apenas um endereço IP. Nomes DNS e MagicDNS não são aceitos.
- IPv4 e IPv6 válidos são aceitos. O exemplo visual usa um IPv4 Tailscale, como
  `100.87.71.48`.
- Um botão **Salvar IP** persiste explicitamente o valor.
- O valor permanece salvo ao atualizar ou fechar a aplicação e ao alternar o
  gateway entre `127.0.0.1` e `0.0.0.0`.
- A configuração funciona da mesma forma nos pacotes macOS e Windows porque é
  persistida pelo backend no diretório de dados da aplicação, não no navegador.

Não fazem parte deste escopo:

- descoberta automática do IP por meio do executável Tailscale;
- instalação ou configuração do Tailscale;
- alteração de firewall ou ACLs da tailnet;
- suporte a nomes MagicDNS;
- sincronização da configuração entre computadores diferentes.

## Arquitetura e persistência

O `GatewaySettingsService` continua sendo o proprietário das configurações de
rede do gateway. A seção `gateway` do `config.json` passa a preservar dois
campos independentes:

```json
{
  "gateway": {
    "host": "0.0.0.0",
    "tailscale_ip": "100.87.71.48"
  }
}
```

Salvar o bind não pode apagar `tailscale_ip`, e salvar o IP não pode alterar o
bind. A leitura das configurações retorna `tailscale_ip` como string ou `null`.
O reset global existente remove a seção persistida e, portanto, também restaura
o IP Tailscale para vazio.

O contrato HTTP do gateway recebe uma operação dedicada para evitar que a tela
**Conectar** precise reenviar ou inferir o bind desejado:

- `PUT /api/gateway/tailscale-ip` com `{ "tailscale_ip": "100.87.71.48" }`;
- resposta no mesmo formato das configurações do gateway;
- IP vazio ou sintaticamente inválido retorna `422` com uma mensagem clara.

## Interface e fluxo de dados

Ao entrar na tela **Conectar**, o frontend carrega as configurações do gateway
e preenche o campo com `tailscale_ip`. Quando o usuário pressiona **Salvar IP**:

1. o frontend remove espaços nas extremidades;
2. envia o valor ao endpoint dedicado;
3. substitui o estado local pela resposta persistida;
4. mostra confirmação acessível de sucesso ou o erro retornado pelo backend.

Enquanto o gateway usa `127.0.0.1`, o campo de IP não aparece e os comandos
continuam apontando para `http://127.0.0.1:11435`. O IP salvo não é apagado.

Quando o gateway usa `0.0.0.0`, os comandos usam o IP persistido:

```bash
export OLLAMA_HOST=http://100.87.71.48:11435
ollama run qwen3.6:35b-a3b-nvfp4 --verbose
```

```powershell
$env:OLLAMA_HOST="http://100.87.71.48:11435"
ollama run qwen3.6:35b-a3b-nvfp4 --verbose
```

Para IPv6, o endereço recebe colchetes ao formar a URL, por exemplo
`http://[fd7a:115c:a1e0::1]:11435`.

Se o gateway estiver em modo de rede e não houver IP persistido, os cards não
copiam um comando com marcador. A interface mantém o foco no campo e informa:
**Informe e salve o IP Tailscale antes de copiar o comando.** Um IP digitado mas
ainda não salvo também não é usado nos comandos, deixando explícito que o valor
persistido é a fonte de verdade.

## Validação e segurança

- O backend valida o valor com uma biblioteca de endereços IP, sem restringir a
  faixa `100.64.0.0/10`; tailnets também podem usar IPv6.
- Esquema, porta, caminho, hostname, credenciais e espaços internos são
  rejeitados.
- O frontend pode oferecer validação antecipada, mas a validação autoritativa é
  sempre a do backend.
- Salvar o IP não reinicia o gateway porque o valor é um endereço de cliente,
  não um endereço de bind.
- Nenhum processo Tailscale é executado e nenhum segredo é armazenado.

## Tratamento de erros

- Falha ao carregar: o campo permanece utilizável, mas exibe que o valor salvo
  não pôde ser consultado; copiar em modo de rede permanece bloqueado.
- IP inválido: mensagem específica junto ao campo e nenhuma alteração no valor
  persistido.
- Falha de gravação: o valor anterior continua como fonte dos comandos e a
  interface informa que o novo IP não foi salvo.
- Gateway parado: mantém o aviso operacional atual; isso não impede salvar o IP.

## Testes e critérios de aceitação

1. O backend salva e recarrega `tailscale_ip` no `config.json`.
2. Atualizar somente `host` preserva o IP; atualizar somente o IP preserva o
   host.
3. IPv4 e IPv6 válidos são aceitos; hostnames, URLs, portas e valores vazios são
   rejeitados com `422`.
4. A tela carrega e apresenta o IP persistido no modo `0.0.0.0`.
5. Recarregar a tela restaura o valor retornado pelo backend.
6. O modo local continua gerando `127.0.0.1:11435` e não apaga o IP salvo.
7. O modo de rede gera a URL com o IP salvo, incluindo colchetes para IPv6.
8. macOS/Linux usa `export`; Windows PowerShell usa `$env:OLLAMA_HOST`.
9. Sem IP salvo, copiar é bloqueado e nenhuma string `<IP_TAILSCALE>` chega à
   área de transferência.
10. Testes unitários e de integração do backend, testes de componentes do
    frontend, typecheck e build passam.
