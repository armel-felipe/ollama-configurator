param(
  [string]$Output = "dist/windows",
  [switch]$SkipFrontendInstall,
  [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
$OutputPath = Join-Path $Root $Output
$Payload = Join-Path $OutputPath "payload"
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
if (Test-Path $Payload) { Remove-Item $Payload -Recurse -Force }

& uv run python (Join-Path $Root "scripts/build_backend.py") --output (Join-Path $OutputPath "backend")
if (-not (Test-Path (Join-Path $OutputPath "backend/OllamaConfiguratorBackend"))) {
  throw "Backend build did not produce OllamaConfiguratorBackend."
}
$FrontendArgs = @("--output", (Join-Path $OutputPath "frontend"))
if ($SkipFrontendInstall) { $FrontendArgs += "--skip-install" }
if ($SkipFrontendBuild) { $FrontendArgs += "--skip-build" }
& node (Join-Path $Root "scripts/build_frontend.mjs") @FrontendArgs
if (-not (Test-Path (Join-Path $OutputPath "frontend/manifest.json"))) {
  throw "Frontend build did not produce manifest.json."
}

New-Item -ItemType Directory -Force -Path $Payload | Out-Null
Copy-Item -Path (Join-Path $OutputPath "backend") -Destination $Payload -Recurse -Force
Copy-Item -Path (Join-Path $OutputPath "frontend") -Destination $Payload -Recurse -Force
Copy-Item -Path (Join-Path $PSScriptRoot "install.ps1") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "uninstall.ps1") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "run.ps1") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "install.bat") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "uninstall.bat") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "run.bat") -Destination $OutputPath -Force
Copy-Item -Path (Join-Path $PSScriptRoot "README-release.md") -Destination (Join-Path $OutputPath "README.md") -Force
Compress-Archive -Path (Join-Path $Payload "*"), (Join-Path $OutputPath "README.md"), (Join-Path $OutputPath "install.ps1"), (Join-Path $OutputPath "uninstall.ps1"), (Join-Path $OutputPath "run.ps1"), (Join-Path $OutputPath "install.bat"), (Join-Path $OutputPath "uninstall.bat"), (Join-Path $OutputPath "run.bat") -DestinationPath (Join-Path $OutputPath "OllamaConfigurator-Windows-x64.zip") -Force
Write-Host "Windows portable installer staged at $OutputPath"
