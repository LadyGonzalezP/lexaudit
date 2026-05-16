"""Configuración central de LexAudit.

Toda la configuración del sistema vive acá, en un solo lugar. Los valores
sensibles (las API keys) se leen del archivo .env; el resto tiene valores por
defecto razonables. Los parámetros legales que cambian cada año (SMMLV,
jornada) se centralizan aquí para poder actualizarlos sin tocar el código.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del proyecto: lexaudit/ (este archivo está en src/lexaudit/config.py)
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuración tipada del sistema. Lee el archivo .env automáticamente."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Proveedor de LLM (agnóstico) ---
    # Validado por tipo: solo "groq" o "gemini". Otro valor falla al arrancar.
    llm_provider: Literal["groq", "gemini"] = "groq"

    # Groq — free tier amplio, usado para los agentes (chat)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Google Gemini — usado para los embeddings del RAG (y opcional como chat)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"

    # --- Rutas ---
    corpus_dir: Path = ROOT_DIR / "corpus"
    chroma_dir: Path = ROOT_DIR / "data" / "chroma"

    # --- RAG ---
    retrieval_top_k: int = 3

    # --- Parámetros legales (cambian por año / decreto — actualizar aquí) ---
    # SMMLV 2026: Salario Mínimo Mensual Legal Vigente (verificado, decreto 2026).
    smmlv: int = 1_750_905
    jornada_max_semanal: int = 44  # horas — 44h hasta 14-jul-2026, 42h después

    # --- Verificador ---
    max_reintentos_verificacion: int = 2


settings = Settings()  # instancia única, se importa desde el resto del código
