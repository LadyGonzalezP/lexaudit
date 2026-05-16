"""Proveedor del modelo de lenguaje (Google Gemini).

Centraliza la creación del LLM en un solo lugar. Si mañana se cambia de
proveedor, solo se toca este archivo: los agentes piden el modelo aquí y no
saben (ni les importa) que por debajo es Gemini.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from lexaudit.config import settings


def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """Devuelve el modelo de chat configurado.

    La temperatura es 0 por defecto: el sistema necesita respuestas estables y
    reproducibles para que la demo en vivo se comporte igual cada vez.
    """
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
    )
