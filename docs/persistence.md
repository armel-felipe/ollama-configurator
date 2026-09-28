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
