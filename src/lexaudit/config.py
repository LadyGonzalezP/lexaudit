"""Configuración central de LexAudit.

Toda la configuración del sistema vive acá, en un solo lugar. Los valores
sensibles (la API key) se leen del archivo .env; el resto tiene valores por
defecto razonables. Los parámetros legales que cambian cada año (SMMLV,
jornada) se centralizan aquí para poder actualizarlos sin tocar el código.
"""

from pathlib import Path

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

    # --- LLM (Google Gemini) ---
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/gemini-embedding-001"

    # --- Rutas ---
    corpus_dir: Path = ROOT_DIR / "corpus"
    chroma_dir: Path = ROOT_DIR / "data" / "chroma"

    # --- RAG ---
    retrieval_top_k: int = 3

    # --- Parámetros legales (cambian por año / decreto — actualizar aquí) ---
    # SMMLV: Salario Mínimo Mensual Legal Vigente.
    # TODO: confirmar el valor 2026 contra el decreto oficial antes de la entrega.
    smmlv: int = 1_423_500
    jornada_max_semanal: int = 44  # horas — 44h hasta 14-jul-2026, 42h después

    # --- Verificador ---
    max_reintentos_verificacion: int = 2


settings = Settings()  # instancia única, se importa desde el resto del código
