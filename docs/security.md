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
