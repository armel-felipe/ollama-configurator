# Ambiente de desenvolvimento

## macOS e Windows

1. Instale Python 3.12+, Node.js 22+ e Ollama.
2. Instale `uv` conforme a documentação oficial do ambiente.
3. Na raiz do projeto, execute `uv sync`.
4. Execute `cd frontend && npm ci`.
5. Inicie o backend em `127.0.0.1:8787`.
6. Inicie o frontend com `npm run dev`.

O frontend é uma interface web local durante o desenvolvimento. O instalador
final será tratado em uma etapa posterior e não exige comandos Python do usuário.
