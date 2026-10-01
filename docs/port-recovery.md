# Inicialização e conflito na porta 8787

O inicializador reserva a porta antes de iniciar a aplicação e o gateway.
Se houver uma instância do Configurator do mesmo usuário, identificada pelo
executável empacotado ou pelo comando e manifesto do projeto, solicita seu
encerramento e aguarda até oito segundos. Se ela não responder, encerra esse
mesmo processo à força e aguarda mais três segundos. O navegador abre somente
após a API e a interface HTML responderem.

Um processo desconhecido nunca é encerrado automaticamente. Uma página local
no navegador informa a porta, o nome e o PID disponíveis e orienta fechar o
programa, usando o Monitor de Atividade ou o Gerenciador de Tarefas se necessário.
Quando faltam permissões para identificar o processo, a página informa essa
limitação. A mensagem também aparece no terminal. A página não depende da porta
ocupada e não executa comandos fornecidos pelo nome do processo.

A recuperação se aplica ao inicializador empacotado e a `python -m backend`.
O comando direto `uvicorn backend.app:app` é destinado ao desenvolvimento e não
executa a recuperação. Este mecanismo trata a porta da interface (8787), não
muda o gerenciamento do gateway (11435), e não apaga configurações.

Testes automatizados: `tests/unit/test_startup.py` e
`tests/unit/test_backend_entrypoint.py`. Os testes de processos usam portas
efêmeras e uma instância descartável, sem acessar configurações do usuário.
