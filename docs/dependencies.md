# Dependências

## Runtimes mínimos

- Python `>=3.12,<3.14`
- Node.js `22+`
- npm compatível com Node.js 22
- Ollama instalado para testes de integração e uso real

## Backend

As dependências de produção ficam em `pyproject.toml` e são travadas por
`uv.lock`. As dependências de desenvolvimento ficam no grupo `dev`.

## Frontend

As dependências ficam em `frontend/package.json` e são travadas por
`frontend/package-lock.json`. O projeto usa `npm ci` em ambientes limpos.

## Regras

- Toda dependência nova precisa ter propósito documentado e teste que a justifique.
- Lockfiles devem ser commitados junto com alterações nos manifests.
- Dependências de empacotamento não são necessárias para desenvolvimento diário.
- O Ollama é uma dependência externa e é diagnosticado em tempo de execução.
