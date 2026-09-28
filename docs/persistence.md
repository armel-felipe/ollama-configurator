# Persistência

As configurações da aplicação ficam em um arquivo JSON versionado logicamente
por schema. O `ConfigStore` grava em arquivo temporário no mesmo diretório,
faz `fsync` e substitui o arquivo final atomicamente.

`null` e o marcador `default` significam ausência de override. Valores como
`0` e `false` são configurações explícitas e permanecem salvos.

Os arquivos da aplicação e os dados do usuário são separados. A localização
é abstraída por `backend.persistence.paths.user_data_dir`.

As configurações por modelo ficam no campo `models`, indexadas pelo identificador
completo do modelo, incluindo tags como `qwen:latest`. A aplicação só envia
parâmetros explicitamente personalizados para o Ollama; parâmetros em Default
são omitidos do payload runtime.

Restaurar configurações remove apenas os overrides salvos no arquivo da
aplicação. A operação não remove modelos, não altera o servidor Ollama e não
apaga arquivos fora do diretório de dados da aplicação. A reconciliação mantém
configurações salvas de modelos que não estão instalados, marcando-os como
ausentes para que possam ser reconhecidos quando forem instalados novamente.

O perfil `think` também é salvo por modelo somente quando o valor é suportado
pela especificação retornada por `/api/show`. A aplicação não inventa níveis
de reasoning. Durante a aplicação, o runner é descarregado e recarregado para
que mudanças de contexto sejam observáveis em `/api/ps`; parâmetros que o
Ollama não publica nesse endpoint permanecem identificados como perfil enviado,
sem serem apresentados como uma medição falsa do runtime.
