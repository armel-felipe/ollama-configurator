param(
  [string]$InstallDir = "$env:LOCALAPPDATA\Ollama Configurator"
)

$ErrorActionPreference = "Stop"
if (Test-Path $InstallDir) {
  Remove-Item -Path $InstallDir -Recurse -Force
}
Write-Host "Ollama Configurator removido. Modelos do Ollama não foram alterados."
