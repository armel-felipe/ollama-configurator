# Empacotamento

O release é construído em duas camadas:

1. `scripts/build_backend.py` gera o executável do backend com PyInstaller e
   grava um manifesto com versão, bind local e portas oficiais.
2. `scripts/build_frontend.mjs` executa `npm ci`, compila o frontend a partir do
   lockfile e copia o `dist` para o artefato final.

## Desenvolvimento e smoke test

```bash
uv run python scripts/build_backend.py --dry-run
node scripts/build_frontend.mjs --dry-run
uv run pytest tests/packaging/test_packaging_smoke.py
```

O build real exige PyInstaller instalado no ambiente de release:

```bash
python -m pip install pyinstaller
bash packaging/macos/build-app.sh
```

No Windows, execute PowerShell como usuário normal:

```powershell
python -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File packaging/windows/build-installer.ps1
```

Os workflows do GitHub Actions repetem esses passos em runners nativos. O
artefato macOS é um `.app` e, quando `hdiutil` está disponível, um `.dmg`; o
Windows produz um pacote portátil `.zip` com scripts de instalação. Um
instalador `.exe` assinado ainda é uma etapa de publicação posterior.

Em todos os casos, o serviço permanece local-only por padrão (`127.0.0.1`),
com o gateway em `11435`. A exposição via Tailscale é uma decisão explícita
na UI: o usuário salva `0.0.0.0` como bind e aplica a alteração, o que reinicia
somente o gateway. O cliente remoto usa o IP Tailscale real da máquina
servidora; essa configuração não é um efeito colateral do instalador.
