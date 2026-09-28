# Segurança e operações destrutivas

O configurador administra apenas configurações locais do Ollama. Os comandos
de restauração são deliberadamente limitados:

- restaurar um modelo remove seus overrides salvos e volta ao comportamento
  Default do Ollama;
- restaurar todos os modelos remove todos os overrides salvos;
- nenhuma dessas operações remove modelos instalados, prompts, arquivos do
  usuário ou a instalação do Ollama;
- a interface exige confirmação antes de executar uma restauração;
- a persistência usa escrita atômica para evitar um arquivo parcialmente
  gravado em caso de interrupção.

Modelos salvos que não aparecem na lista atual do Ollama são preservados e
marcados como ausentes pela camada de reconciliação. Isso evita perda de
configuração quando um modelo é removido temporariamente ou quando o servidor
está indisponível.
# Segurança do gateway

O gateway não deve ser exposto diretamente à internet. O padrão é bind em
`127.0.0.1:11435`. Para acesso por Tailscale, o bind deve ser explícito no IP
Tailscale do host e `OLLAMA_GATEWAY_API_KEY` deve estar definido.

A autenticação aceita `x-api-key` ou `Authorization: Bearer <chave>`. A porta
original do Ollama (`11434`) deve continuar restrita ao host. ACLs do Tailscale e
firewall do sistema continuam sendo camadas adicionais; a chave do gateway não
substitui essas políticas.
