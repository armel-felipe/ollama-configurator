# PRD — Ollama Configurator

**Status:** Draft v0.1  
**Produto:** Ollama Configurator  
**Tipo:** Aplicação local multiplataforma para configuração, persistência, diagnóstico e benchmark de modelos Ollama  
**Plataformas iniciais:** macOS e Windows  
**Backend:** Python  
**Interface:** Web UI local  
**Distribuição:** GitHub público + GitHub Releases  

---

## 1. Visão do produto

O **Ollama Configurator** será uma aplicação local, multiplataforma, destinada a facilitar a configuração de modelos Ollama e dos parâmetros do servidor Ollama por meio de uma interface gráfica simples, didática e segura.

O produto deverá abstrair a necessidade de o usuário conhecer comandos de terminal, variáveis de ambiente, Modelfiles ou detalhes específicos de macOS e Windows.

A aplicação deverá detectar automaticamente o sistema operacional, hardware disponível, backend de aceleração compatível e modelos Ollama existentes na máquina, apresentando somente configurações válidas para aquele ambiente.

O foco inicial será:

- configuração de parâmetros de servidor;
- configuração de parâmetros por modelo;
- persistência dessas configurações;
- restauração segura dos padrões do Ollama;
- identificação de hardware;
- sugestões contextualizadas;
- benchmark de desempenho;
- diagnóstico do ambiente Ollama.

---

# 2. Objetivos

## 2.1 Objetivo principal

Criar uma interface gráfica local para administrar configurações do Ollama sem depender de edição manual de arquivos, Modelfiles ou comandos de terminal.

## 2.2 Objetivos específicos

A aplicação deve permitir:

1. Detectar automaticamente o Ollama instalado.
2. Identificar a versão do Ollama.
3. Listar dinamicamente todos os modelos Ollama baixados na máquina.
4. Atualizar essa lista sempre que a interface for recarregada ou atualizada.
5. Exibir informações básicas dos modelos:
   - nome;
   - tamanho;
   - família;
   - quantização;
   - outras informações expostas pela API.
6. Configurar parâmetros por modelo.
7. Persistir configurações por modelo.
8. Configurar parâmetros globais do servidor Ollama.
9. Persistir parâmetros de servidor mesmo após reboot.
10. Permitir restaurar parâmetros individualmente para **Ollama Default**.
11. Oferecer um botão para restaurar **todos os parâmetros de todos os modelos** para Ollama Default.
12. Oferecer um botão separado para restaurar **todos os parâmetros do servidor** para Ollama Default.
13. Detectar hardware e exibir apenas opções compatíveis.
14. Exibir descrições curtas e didáticas sobre cada configuração.
15. Executar benchmarks de desempenho.
16. Exibir diagnóstico do ambiente.
17. Operar exclusivamente de forma local por padrão.

---

# 3. Princípios do produto

## 3.1 Local-first

A aplicação deverá operar localmente.

A arquitetura padrão será:

```text
Browser local
     ↓
127.0.0.1
     ↓
Backend Python
     ↓
Ollama local
```

O backend não deverá escutar em `0.0.0.0` por padrão.

A aplicação não deverá depender de um servidor remoto para funcionamento.

---

## 3.2 Não destrutivo

A aplicação não deverá modificar permanentemente os modelos originais salvo quando essa funcionalidade for explicitamente adicionada no futuro.

Os parâmetros de modelo deverão preferencialmente ser aplicados em runtime pela API Ollama.

---

## 3.3 Default significa ausência de override

A aplicação deverá distinguir claramente:

```text
Default
```

de:

```text
false
0
4096
f16
etc.
```

Quando um parâmetro estiver como **Ollama Default**, a aplicação deverá deixar de enviar ou definir esse parâmetro.

Exemplo conceitual:

```json
{
  "num_ctx": null
}
```

significa:

```text
não sobrescrever o comportamento do Ollama
```

---

## 3.4 Hardware-aware

A aplicação não deverá apresentar opções sem sentido para o hardware detectado.

Exemplo:

### Apple Silicon

Exibir:

```text
Metal
```

Não exibir como opção de otimização:

```text
CUDA
ROCm
Vulkan
```

quando esses backends não forem aplicáveis.

### NVIDIA

Poderão ser apresentadas, conforme compatibilidade:

```text
CUDA
Vulkan
```

### AMD

Poderão ser apresentadas, conforme SO e suporte:

```text
ROCm
Vulkan
Integrated GPU options
```

---

# 4. Repositório e distribuição

## 4.1 Repositório GitHub

O projeto deverá possuir um repositório dedicado no GitHub.

Nome recomendado:

```text
ollama-configurator
```

### Requisito

O repositório deverá ser criado com perfil:

```text
PUBLIC
```

Motivos:

- facilitar distribuição;
- permitir colaboração;
- centralizar documentação;
- disponibilizar releases;
- disponibilizar instaladores;
- permitir auditoria do código;
- facilitar issues e contribuições futuras.

O GitHub será utilizado para:

- código-fonte;
- versionamento;
- documentação;
- issues;
- changelog;
- releases;
- distribuição de instaladores.

O GitHub **não deverá participar da operação cotidiana da aplicação local**.

---

# 5. Estratégia de desenvolvimento local

O projeto deverá ser desenvolvido em uma pasta local da máquina de desenvolvimento.

Evitar:

```text
pastas de rede
shares
volumes remotos
```

para o ambiente principal de desenvolvimento.

Isso é especialmente importante porque a aplicação deverá:

- detectar hardware local;
- interagir com o Ollama local;
- reiniciar processos locais;
- testar persistência do sistema operacional;
- medir desempenho real;
- criar arquivos locais;
- trabalhar com variáveis de ambiente.

Fluxo recomendado:

```text
GitHub
   ↓
git clone
   ↓
pasta local
   ↓
desenvolvimento
   ↓
commit
   ↓
push
```

---

# 6. Arquitetura proposta

```text
ollama-configurator/
│
├── backend/
│   ├── app.py
│   │
│   ├── ollama/
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── server.py
│   │   └── benchmark.py
│   │
│   ├── hardware/
│   │   ├── detector.py
│   │   └── capabilities.py
│   │
│   ├── persistence/
│   │   ├── config_store.py
│   │   └── profiles.py
│   │
│   ├── os_adapters/
│   │   ├── base.py
│   │   ├── macos.py
│   │   └── windows.py
│   │
│   └── diagnostics/
│       └── service.py
│
├── frontend/
│
├── scripts/
│   ├── macos/
│   └── windows/
│
├── tests/
│
├── docs/
│
├── PRD.md
├── README.md
└── requirements.txt
```

---

# 7. Backend

## 7.1 Tecnologia

Backend inicial:

```text
Python + FastAPI
```

Motivos:

- multiplataforma;
- rápido desenvolvimento;
- boa integração com APIs;
- fácil acesso ao sistema operacional;
- adequado para benchmark e coleta de métricas;
- simples integração com frontend web local.

---

# 8. Interface

A interface será inicialmente uma aplicação web local.

Exemplo:

```text
http://127.0.0.1:8787
```

O usuário não deverá precisar iniciar manualmente comandos Python no uso normal após a instalação.

---

# 9. Descoberta dinâmica de modelos

A aplicação deverá consultar o Ollama local para identificar os modelos instalados.

A lista deverá ser atualizada:

- ao abrir a aplicação;
- ao atualizar a página;
- através de um botão "Atualizar modelos";
- após operações que possam modificar a lista.

O estado salvo da aplicação deverá ser cruzado com a lista real dos modelos existentes.

Exemplo:

```text
Qwen 27B
Configuração salva ✓

Gemma 27B
Ollama Default

Modelo antigo
Não instalado
```

Configurações de modelos removidos não precisam ser apagadas automaticamente.

Podem ser marcadas como:

```text
model_missing
```

permitindo sua reutilização caso o modelo volte a ser instalado.

---

# 10. Configuração de modelos

A interface deverá possuir duas camadas:

## Basic

Inicialmente:

- Context Window / `num_ctx`
- Temperature
- Max Output Tokens
- Thinking, quando suportado
- Keep Alive quando pertinente

## Advanced

Possíveis parâmetros:

- `num_ctx`
- `num_batch`
- `num_gpu`
- `main_gpu`
- `num_thread`
- `top_k`
- `top_p`
- `min_p`
- `temperature`
- `repeat_last_n`
- `repeat_penalty`
- `presence_penalty`
- `frequency_penalty`
- `seed`
- `num_predict`
- `stop`

Somente parâmetros efetivamente suportados pela versão utilizada deverão ser apresentados.

---

# 11. Perfis de configuração

Deverá ser possível criar perfis opcionais como:

```text
Default
Fast
Agent
Long Context
Coding
Custom
```

Os perfis não deverão exigir duplicação dos pesos do modelo.

Exemplo conceitual:

```json
{
  "model": "qwen",
  "profile": "Fast",
  "options": {
    "num_ctx": 32768,
    "temperature": 0.2
  }
}
```

---

# 12. Persistência dos parâmetros de modelo

Parâmetros enviados apenas pela API Ollama não são naturalmente permanentes.

Portanto, a aplicação deverá manter seu próprio armazenamento persistente.

Exemplo:

```json
{
  "models": {
    "qwen": {
      "num_ctx": 32768,
      "temperature": 0.2
    }
  }
}
```

Ao utilizar um modelo através da aplicação, os overrides deverão ser reaplicados.

---

# 13. Ollama Default por modelo

Cada parâmetro deve aceitar:

```text
Ollama Default
```

Quando selecionado, o override deverá ser removido.

Exemplo:

```text
Temperature
● Ollama Default
○ Custom: 0.2
```

---

# 14. Reset global dos modelos

Deverá existir:

```text
Restaurar TODOS os modelos para Ollama Default
```

Essa ação deverá:

- remover todos os overrides salvos dos modelos;
- não remover os modelos;
- não alterar pesos;
- não excluir downloads Ollama.

Deverá haver confirmação antes da execução.

---

# 15. Configuração do servidor Ollama

A interface deverá suportar, conforme disponibilidade da versão Ollama:

- Flash Attention;
- KV Cache Type;
- Global Context;
- Keep Alive;
- Parallel Requests;
- Max Loaded Models;
- Max Queue;
- GPU Overhead;
- Scheduler settings;
- Integrated GPU settings;
- backend-related options;
- outras opções suportadas.

---

# 16. Persistência dos parâmetros do servidor

Este é um requisito obrigatório.

Alterações de servidor não poderão depender apenas de:

```bash
export VAR=value
```

ou de uma sessão de terminal.

A aplicação deverá utilizar mecanismos persistentes adequados a cada sistema operacional.

---

# 17. OS Adapters

Deverá existir uma interface comum:

```python
class SystemAdapter:
    def set_environment_variable(...)
    def remove_environment_variable(...)
    def get_environment_variable(...)
    def restart_ollama(...)
    def detect_gpu(...)
    def detect_memory(...)
```

Implementações iniciais:

```text
MacOSAdapter
WindowsAdapter
```

Possível futuramente:

```text
LinuxAdapter
```

---

# 18. Persistência macOS

A implementação para macOS deverá considerar os mecanismos adequados de persistência da sessão gráfica e inicialização.

A solução poderá envolver:

- LaunchAgent;
- launchctl;
- arquivo de configuração gerenciado pela aplicação;
- inicialização/reinicialização controlada do Ollama.

A configuração deve sobreviver a:

```text
fechamento do Ollama
logout/login
reboot
```

---

# 19. Persistência Windows

A implementação Windows deverá utilizar mecanismo apropriado para variáveis persistentes do usuário ou sistema.

A configuração deve sobreviver a:

```text
fechamento do Ollama
logout/login
reboot
```

---

# 20. Reset do servidor

Deverá existir:

```text
Restaurar servidor para Ollama Default
```

Essa ação deverá remover os overrides criados pela aplicação.

Importante:

```text
Default = remover a variável
```

e não:

```text
atribuir zero, false ou outro valor arbitrário
```

---

# 21. Factory Reset

Poderá existir:

```text
Restaurar toda a configuração
```

A ação deverá:

- resetar parâmetros dos modelos;
- resetar parâmetros do servidor;
- remover perfis personalizados.

Histórico de benchmark poderá ser preservado.

---

# 22. Explicações didáticas

Cada parâmetro deverá conter uma descrição curta.

Exemplo:

```text
KV Cache — Q8_0

Reduz aproximadamente o uso de memória do KV cache
quando comparado a F16, mantendo boa precisão na maioria
dos modelos. É especialmente útil em contextos maiores.
```

Evitar recomendações rígidas como:

```text
Q8 somente para GPUs entre X e Y GB
```

porque consumo depende de:

- tamanho do modelo;
- arquitetura;
- quantização dos pesos;
- contexto;
- KV cache;
- concorrência.

---

# 23. Recomendações contextualizadas

Quando possível, o sistema deverá usar o hardware e a configuração atual para gerar recomendações.

Exemplo:

```text
Q8_0 — Recommended

Hardware:
Apple M3 Pro
36 GB Unified Memory

Modelo:
27B Q4

Context:
64K

Motivo:
bom equilíbrio entre memória e precisão para esta configuração.
```

---

# 24. Labels de orientação

A interface poderá utilizar:

```text
Default
Recommended
Performance
Memory Saver
Quality
Advanced
Experimental
```

---

# 25. Hardware detection

A aplicação deverá detectar:

- SO;
- arquitetura;
- CPU;
- memória RAM;
- memória unificada quando aplicável;
- GPU;
- fabricante;
- backend disponível;
- versão Ollama.

---

# 26. Backend de GPU

A interface deverá apresentar somente opções plausíveis.

Exemplos:

## Apple Silicon

```text
Metal
```

## NVIDIA

```text
Auto
CUDA
Vulkan
```

quando aplicável.

## AMD

```text
Auto
ROCm
Vulkan
```

quando aplicável.

---

# 27. Validação

A aplicação nunca deverá assumir que determinado parâmetro existe.

A UI deverá ser construída com base em:

```text
versão Ollama
+
SO
+
hardware
+
capabilities
```

---

# 28. Benchmark

O produto deverá oferecer benchmark integrado.

Métricas iniciais:

- model load time;
- prompt processing tokens/s;
- generation tokens/s;
- total duration;
- time to first token quando possível;
- RAM utilizada;
- VRAM/unified memory quando possível;
- utilização GPU quando possível.

Exemplo:

```text
Configuration A

Prompt:       615 t/s
Generation:   24.8 t/s
RAM:          21.4 GB
GPU:          100%
Load:         8.2 s
```

---

# 29. Comparação de configurações

A interface deverá permitir comparar resultados.

Exemplo:

```text
                    A          B

Context             32K        64K
KV                   Q8         Q8
Flash Attention      ON         ON

Prompt t/s          615        430
Generation t/s      24.8       23.9
Memory              21 GB      25 GB
```

---

# 30. Diagnostics

Tela proposta:

```text
OLLAMA DIAGNOSTICS

Ollama Version
Server Status
API Status
OS
CPU
GPU
Memory
Backend
Loaded Models
Processor Allocation
Context
Flash Attention
KV Cache
```

Ações possíveis:

```text
Copy diagnostics
Refresh
Restart Ollama
Open logs
```

---

# 31. Segurança

A aplicação deverá seguir:

## 31.1 Localhost only

Backend:

```text
127.0.0.1
```

por padrão.

## 31.2 Sem shell arbitrário

Não criar endpoint como:

```text
POST /run-command
```

capaz de executar comandos arbitrários.

Utilizar operações explícitas:

```text
POST /server/restart
POST /server/settings
POST /models/{id}/settings
POST /reset/models
POST /reset/server
```

## 31.3 Menor privilégio possível

A aplicação deverá solicitar apenas permissões necessárias.

---

# 32. Instalação

Durante desenvolvimento:

```text
git clone
install dependencies
run local application
```

Posteriormente:

## macOS

Possíveis formatos:

```text
.dmg
.pkg
```

## Windows

Possíveis formatos:

```text
.exe
.msi
```

---

# 33. Diretórios da aplicação

O programa e os dados do usuário deverão ser separados.

Exemplo conceitual:

## macOS

```text
Application
Application Support
```

## Windows

```text
LOCALAPPDATA
APPDATA
```

O backend deverá abstrair isso através de funções multiplataforma.

---

# 34. GitHub Releases

O GitHub deverá ser a fonte oficial de distribuição.

Exemplo:

```text
Release v0.2.0

OllamaConfigurator-macOS-arm64.dmg
OllamaConfigurator-Windows-x64.exe
checksums.txt
```

---

# 35. Atualizações

No futuro a aplicação poderá:

1. consultar a última release pública;
2. comparar com sua versão;
3. informar que existe atualização;
4. abrir ou iniciar o fluxo de atualização.

A aplicação não deverá enviar configurações locais ao GitHub para realizar essa verificação.

---

# 36. MVP

## MVP 0.1

Entregar:

- backend FastAPI;
- frontend local básico;
- detecção macOS/Windows;
- conexão com Ollama local;
- listagem dinâmica de modelos;
- informações do hardware;
- configuração básica por modelo;
- configuração básica do servidor;
- armazenamento persistente;
- Ollama Default por parâmetro;
- reset global dos modelos;
- reset global do servidor;
- restart Ollama;
- diagnostics básicos.

---

# 37. MVP 0.2

Adicionar:

- Advanced settings;
- profiles;
- recomendações contextualizadas;
- benchmark;
- comparação de benchmarks;
- melhor detecção de GPU;
- explicações didáticas completas.

---

# 38. MVP 0.3

Adicionar:

- instalador macOS;
- instalador Windows;
- GitHub Releases;
- check de atualização;
- logs avançados;
- import/export de configurações.

---

# 39. Futuro

Possibilidades:

- Linux;
- gerenciamento de múltiplas instalações locais;
- presets compartilháveis;
- import/export;
- comparação automática de quantizações;
- estimativa de memória antes de carregar modelo;
- benchmark automatizado de vários modelos;
- integração opcional com APIs compatíveis OpenAI;
- criação opcional de modelos persistentes derivados;
- recomendações específicas para arquiteturas futuras.

---

# 40. Fora do escopo inicial

Não fazem parte do MVP:

- gestão remota via VPS;
- execução de comandos shell arbitrários;
- exposição pública do backend;
- hospedagem SaaS;
- gerenciamento remoto irrestrito de computadores;
- download automático de modelos sem confirmação;
- substituição da interface Ollama completa;
- edição destrutiva dos modelos originais.

---

# 41. Critérios de aceitação

O MVP será considerado funcional quando:

1. A aplicação iniciar em macOS e Windows.
2. Identificar o Ollama local.
3. Identificar corretamente os modelos instalados.
4. Atualizar a lista quando modelos forem adicionados/removidos.
5. Exibir SO, CPU, GPU e memória.
6. Exibir somente configurações plausíveis para o hardware.
7. Permitir alterar parâmetros de modelo.
8. Manter parâmetros de modelo após reiniciar a aplicação.
9. Permitir configurar parâmetros do servidor.
10. Manter parâmetros do servidor após reboot.
11. Permitir restaurar um parâmetro para Ollama Default.
12. Permitir restaurar todos os modelos para Ollama Default.
13. Permitir restaurar o servidor para Ollama Default.
14. Não remover modelos durante um reset de configuração.
15. Escutar apenas localhost por padrão.
16. Não oferecer execução arbitrária de shell.
17. Exibir descrição das opções configuráveis.
18. Reiniciar corretamente o Ollama quando necessário.

---

# 42. Decisões já tomadas

- Backend: **Python**
- API/framework sugerido: **FastAPI**
- UI: **web local**
- Execução: **local-first**
- Sistemas iniciais: **macOS e Windows**
- Desenvolvimento: **pasta local**
- GitHub: **repositório público**
- Distribuição futura: **GitHub Releases**
- Modelos: **descoberta dinâmica**
- Configurações: **persistentes**
- Default: **ausência de override**
- Hardware: **detecção automática**
- GPU settings: **mostrar apenas quando fizerem sentido**
- Segurança: **localhost-only por padrão**
- Gestão remota/VPS: **fora do escopo inicial**

---

# 43. Próximo passo recomendado

1. Criar o repositório público `ollama-configurator`.
2. Adicionar este `PRD.md`.
3. Criar `README.md`.
4. Clonar o projeto para uma pasta local no computador de desenvolvimento.
5. Criar skeleton do backend FastAPI.
6. Implementar descoberta do Ollama e `/api/tags`.
7. Implementar detecção de hardware.
8. Criar o primeiro `MacOSAdapter` e `WindowsAdapter`.
9. Implementar configuração persistente.
10. Criar a primeira tela funcional.

