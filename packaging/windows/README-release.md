# Ollama Configurator v0.1.11 — Windows x64

## Português

Extraia todo o ZIP e abra o PowerShell nessa pasta. Execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
.\run.ps1
```

A instalação usa `%LOCALAPPDATA%\Ollama Configurator`. Para remover:

```powershell
.\uninstall.ps1
```

A interface usa a porta 8787 e o gateway Ollama usa a porta 11435. Uma instância anterior do Configurator pode ser substituída automaticamente. Outro programa não será encerrado: a aplicação mostrará seu nome e PID.

## English

Extract the entire ZIP and open PowerShell in that folder. Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
.\run.ps1
```

The default install path is `%LOCALAPPDATA%\Ollama Configurator`. To remove it:

```powershell
.\uninstall.ps1
```

The interface uses port 8787 and the Ollama gateway uses port 11435. A previous Configurator instance may be replaced automatically. An unrelated program is preserved and its name and PID are shown.
