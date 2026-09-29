from typing import Any

SERVER_SETTINGS: dict[str, dict[str, Any]] = {
    "OLLAMA_KV_CACHE_TYPE": {
        "label": "KV cache",
        "description": "Precisão usada para armazenar o cache de atenção.",
        "type": "select",
        "options": ["f16", "q8_0", "q4_0"],
        "default": "f16",
    },
    "OLLAMA_FLASH_ATTENTION": {
        "label": "Flash Attention",
        "description": "Otimiza atenção quando suportado pelo backend.",
        "type": "boolean",
        "default": False,
    },
    "OLLAMA_CONTEXT_LENGTH": {
        "label": "Contexto global",
        "description": "Limite padrão de contexto do servidor Ollama.",
        "type": "number",
        "default": 4096,
        "min": 1,
    },
    "OLLAMA_KEEP_ALIVE": {
        "label": "Keep Alive global",
        "description": "Tempo padrão para manter modelos carregados.",
        "type": "text",
        "default": "5m",
    },
    "OLLAMA_NUM_PARALLEL": {
        "label": "Execuções paralelas",
        "description": "Número máximo de requisições processadas em paralelo.",
        "type": "number",
        "default": 1,
        "min": 1,
    },
    "OLLAMA_MAX_LOADED_MODELS": {
        "label": "Modelos carregados",
        "description": "Quantidade máxima de modelos residentes.",
        "type": "number",
        "default": 1,
        "min": 1,
    },
    "OLLAMA_MAX_QUEUE": {
        "label": "Fila máxima",
        "description": "Quantidade máxima de requisições aguardando.",
        "type": "number",
        "default": 512,
        "min": 1,
    },
    "OLLAMA_GPU_OVERHEAD": {
        "label": "GPU overhead",
        "description": "Memória reservada para outras operações da GPU.",
        "type": "number",
        "default": 0,
        "min": 0,
    },
    "OLLAMA_SCHED_SPREAD": {
        "label": "Distribuir scheduler",
        "description": "Distribui modelos entre dispositivos quando disponível.",
        "type": "boolean",
        "default": False,
    },
}


def public_catalog() -> dict[str, dict[str, Any]]:
    return {name: dict(metadata) for name, metadata in SERVER_SETTINGS.items()}


def parse_environment(name: str, value: str) -> Any:
    metadata = SERVER_SETTINGS[name]
    if metadata["type"] == "boolean":
        return value.lower() == "true"
    if metadata["type"] == "number":
        return int(value)
    return value


def validate_setting(name: str, value: Any) -> Any:
    if name not in SERVER_SETTINGS:
        raise ValueError(f"configuração global desconhecida: {name}")
    if value == "default":
        return value
    metadata = SERVER_SETTINGS[name]
    if metadata["type"] == "select":
        if not isinstance(value, str) or value not in metadata["options"]:
            raise ValueError("KV cache possui um valor não suportado")
    elif metadata["type"] == "boolean":
        if not isinstance(value, bool):
            raise ValueError(f"{name} deve ser booleano")
    elif metadata["type"] == "number":
        if isinstance(value, bool) or not isinstance(value, int) or value < metadata["min"]:
            raise ValueError(f"{name} deve ser um inteiro válido")
    elif not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} deve ser texto não vazio")
    return value
