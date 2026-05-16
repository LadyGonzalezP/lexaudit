"""Ingesta del corpus normativo al vector store.

Lee las fichas Markdown de `corpus/`, las convierte en documentos y las indexa
en ChromaDB. Cada ficha se indexa como una unidad: son cortas y autocontenidas,
trocearlas partiría la unidad semántica (norma + regla + ejemplo).

Uso:  uv run python -m lexaudit.rag.ingest
"""

import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document

from lexaudit.config import settings
from lexaudit.rag.vectorstore import COLLECTION_NAME, get_embeddings


def _extraer_tema(texto: str) -> str:
    """Lee la línea '**Tema:** XXX' de una ficha."""
    for linea in texto.splitlines():
        if linea.startswith("**Tema:**"):
            return linea.split("**Tema:**")[1].strip()
    return "DESCONOCIDO"


def cargar_fichas() -> list[Document]:
    """Carga las fichas Markdown del corpus como documentos de LangChain."""
    docs: list[Document] = []
    for ruta in sorted(settings.corpus_dir.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        docs.append(
            Document(
                page_content=texto,
                metadata={"tema": _extraer_tema(texto), "fuente": ruta.name},
            )
        )
    return docs


def ingest() -> None:
    """Reindexa el corpus completo desde cero (operación idempotente)."""
    if settings.chroma_dir.exists():
        shutil.rmtree(settings.chroma_dir)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    (settings.chroma_dir / ".gitkeep").touch()

    docs = cargar_fichas()
    if not docs:
        raise RuntimeError(f"No se encontraron fichas en {settings.corpus_dir}")

    Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(settings.chroma_dir),
    )
    print(f"OK - {len(docs)} fichas indexadas: {[d.metadata['tema'] for d in docs]}")


if __name__ == "__main__":
    ingest()
