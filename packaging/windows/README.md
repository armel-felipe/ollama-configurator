# Windows release bundle

`build-installer.ps1` compila os dois artefatos, monta um payload portátil e
gera um `.zip` com scripts explícitos de instalação e desinstalação.

O instalador grava dados do configurador em `%LOCALAPPDATA%`. A desinstalação
não remove o Ollama, os modelos ou configurações fora do diretório do
configurador. Assinatura Authenticode e validação em máquina limpa são
obrigatórias antes de publicar um `.exe` para usuários finais.
