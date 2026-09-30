# Runbook: Ollama indisponível

## 1. Confirmar o serviço base

Open `http://127.0.0.1:11434` in a browser or use the Ollama application. If
it does not respond, start Ollama using its normal desktop installation.

## 2. Confirmar o Configurator

Start the development launcher from the project root and open
`http://127.0.0.1:5173`. The UI should report the backend on port `8787` and
the managed gateway on port `11435`.

## 3. Read the visible state

- **Gateway ativo — respondendo**: the managed gateway is available.
- **Gateway externo**: another process owns port `11435`; the UI identifies it
  before offering a confirmed release.
- **Aplicação indisponível**: restart the launcher, not Ollama model settings.
- **Runtime não confirmado**: reload the selected model profile and inspect
  `/api/ps` or `ollama ps`.

## 4. Do not bypass the gateway

Clients that must use the saved profile should target
`http://127.0.0.1:11435`. A direct `11434` request is an independent Ollama
session and does not prove that the Configurator profile was applied.
