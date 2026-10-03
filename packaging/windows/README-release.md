# Ollama Configurator v0.1.16 — Windows x64

## Português

Extraia todo o ZIP e execute `install.bat` para instalar. Depois execute `run.bat` para iniciar a aplicação. Esses arquivos chamam os scripts PowerShell incluídos com a política de execução necessária.

Também é possível abrir o PowerShell nessa pasta e executar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
.\run.ps1
```

A instalação usa `%LOCALAPPDATA%\Ollama Configurator`. Para remover, execute `uninstall.bat` ou:

```powershell
.\uninstall.ps1
```

A interface usa a porta 8787 e o gateway Ollama usa a porta 11435. Uma instância anterior do Configurator pode ser substituída automaticamente. Outro programa não será encerrado: a aplicação mostrará seu nome e PID.

## English

Extract the entire ZIP and run `install.bat` to install. Then run `run.bat` to start the application. These files call the included PowerShell scripts with the required execution policy.

You can also open PowerShell in the extracted folder and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
.\run.ps1
```

The default install path is `%LOCALAPPDATA%\Ollama Configurator`. To remove it, run `uninstall.bat` or:

```powershell
.\uninstall.ps1
```

The interface uses port 8787 and the Ollama gateway uses port 11435. A previous Configurator instance may be replaced automatically. An unrelated program is preserved and its name and PID are shown.
