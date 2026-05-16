"""Acceso al vector store (ChromaDB) con embeddings de Google Gemini.

El vector store guarda cada ficha del corpus convertida en un vector numérico
(embedding). Buscar por significado consiste en convertir la consulta en un
vector y encontrar los más cercanos.
"""

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from lexaudit.config import settings

# Nombre de la colección dentro de ChromaDB
COLLECTION_NAME = "corpus_laboral"


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Modelo de embeddings de Gemini (convierte texto en vectores)."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
    )


def get_vectorstore() -> Chroma:
    """Vector store ChromaDB persistido en disco."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(settings.chroma_dir),
    )
