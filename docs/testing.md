# Testing the MVP

## Local gauntlet

Run the backend and frontend checks from the project root:

```text
uv run pytest
uv run ruff check backend tests
uv run mypy backend
cd frontend
npm test -- --run
npm run typecheck
npm run build
git diff --check
```

The acceptance suite lives in `tests/acceptance/` and the local-only security
checks live in `tests/security/`. They use deterministic doubles for the
Ollama boundary; native runtime validation must still be performed against an
installed Ollama as described in the roadmap.

## Native runtime gate

With the launcher running, validate a loaded model through the UI, `/api/ps`,
and the CLI pointed to the managed gateway:

```text
OLLAMA_HOST=http://127.0.0.1:11435 ollama ps
```

Change the context to 16K, 32K, and 64K one at a time, apply the profile, and
confirm the same `CONTEXT` value appears in `ollama ps` after every reload.
