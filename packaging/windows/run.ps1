param(
  [string]$InstallDir = "$env:LOCALAPPDATA\Ollama Configurator"
)

$ErrorActionPreference = "Stop"
$env:OLLAMA_CONFIGURATOR_FRONTEND_DIR = Join-Path $InstallDir "frontend"
$env:OLLAMA_CONFIGURATOR_OPEN_BROWSER = "1"
& (Join-Path $InstallDir "backend\OllamaConfiguratorBackend\OllamaConfiguratorBackend")
