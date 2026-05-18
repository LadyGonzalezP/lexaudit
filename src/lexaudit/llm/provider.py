"""Proveedor del modelo de lenguaje (agnóstico al proveedor).

El sistema soporta dos proveedores —Groq y Google Gemini— y se elige por
configuración (`LLM_PROVIDER`). El resto del código pide el modelo con
`get_llm()` y recibe siempre la misma interfaz (`BaseChatModel` de LangChain):
los agentes no saben —ni necesitan saber— qué proveedor está detrás.

Cambiar de proveedor es cambiar una variable en el archivo .env.
"""

from langchain_core.language_models.chat_models import BaseChatModel

from lexaudit.config import settings


def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """Devuelve el modelo de chat del proveedor configurado.

    Temperatura 0 por defecto: el sistema necesita respuestas estables y
    reproducibles para que la demo en vivo se comporte igual cada vez.

    `max_retries` hace que LangChain reintente automáticamente —con espera
    incremental— ante errores transitorios del proveedor (rate-limit, 5xx).
    """
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
            max_retries=settings.llm_max_retries,
        )

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_retries=settings.llm_max_retries,
    )
