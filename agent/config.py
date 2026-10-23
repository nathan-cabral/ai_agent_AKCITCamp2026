"""Configuração central da integração com modelos de linguagem."""

# A seleção final é feita consultando os modelos disponíveis para a chave.
# A ordem apenas prioriza modelos estáveis e adequados a chat quando disponíveis.
PREFERRED_GEMINI_MODELS = (
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
)

UNSUITABLE_MODEL_MARKERS = (
    "embedding",
    "image",
    "imagen",
    "live",
    "nano-banana",
    "tts",
    "veo",
)

MAX_OUTPUT_TOKENS = 800
TEMPERATURE = 0.3
