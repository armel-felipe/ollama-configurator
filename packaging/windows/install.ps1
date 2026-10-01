param(
  [string]$InstallDir = "$env:LOCALAPPDATA\Ollama Configurator"
)

$ErrorActionPreference = "Stop"
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Path (Join-Path $source "backend") -Destination $InstallDir -Recurse -Force
Copy-Item -Path (Join-Path $source "frontend") -Destination $InstallDir -Recurse -Force
Write-Host "Ollama Configurator instalado em $InstallDir"
