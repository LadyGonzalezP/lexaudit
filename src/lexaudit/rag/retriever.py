"""Recuperación híbrida: búsqueda vectorial (semántica) + BM25 (léxica).

- La búsqueda vectorial entiende el *significado* de la consulta.
- BM25 encuentra coincidencias de *palabras* exactas.
- Las dos listas de resultados se combinan con Reciprocal Rank Fusion (RRF):
  cada documento suma 1/(k + posición) por cada lista en que aparece, así un
  documento bien rankeado por cualquiera de las dos ramas sube en el resultado
  final. RRF es robusto porque no necesita normalizar los puntajes de cada
  rama (que están en escalas distintas), solo usa las posiciones.
"""

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from lexaudit.config import settings
from lexaudit.models.schemas import NormaRecuperada
from lexaudit.rag.ingest import cargar_fichas
from lexaudit.rag.vectorstore import get_vectorstore

# Constante de amortiguación de RRF: reduce el peso de las primeras posiciones.
_RRF_K = 60


def _tokenizar(texto: str) -> list[str]:
    """Tokenización simple para BM25 (suficiente para un corpus curado y chico)."""
    return texto.lower().split()


def recuperar(consulta: str, top_k: int | None = None) -> list[Document]:
    """Recupera las fichas normativas más relevantes para una consulta.

    Combina una rama semántica (vectorial) y una léxica (BM25) con RRF.
    """
    top_k = top_k or settings.retrieval_top_k
    fichas = cargar_fichas()

    # --- Rama semántica: búsqueda vectorial sobre ChromaDB ---
    ranking_vectorial = get_vectorstore().similarity_search(consulta, k=len(fichas))

    # --- Rama léxica: BM25 sobre las mismas fichas ---
    bm25 = BM25Okapi([_tokenizar(f.page_content) for f in fichas])
    puntajes_bm25 = bm25.get_scores(_tokenizar(consulta))
    ranking_bm25 = sorted(
        range(len(fichas)), key=lambda i: puntajes_bm25[i], reverse=True
    )

    # --- Fusión RRF: cada ficha suma 1/(k + posición) por cada ranking ---
    rrf: dict[str, float] = {}
    for posicion, doc in enumerate(ranking_vectorial):
        clave = doc.metadata["fuente"]
        rrf[clave] = rrf.get(clave, 0.0) + 1.0 / (_RRF_K + posicion)
    for posicion, indice in enumerate(ranking_bm25):
        clave = fichas[indice].metadata["fuente"]
        rrf[clave] = rrf.get(clave, 0.0) + 1.0 / (_RRF_K + posicion)

    # --- Ordenar las fichas por puntaje RRF y devolver las mejores ---
    por_fuente = {f.metadata["fuente"]: f for f in fichas}
    ordenadas = sorted(
        por_fuente.values(),
        key=lambda f: rrf.get(f.metadata["fuente"], 0.0),
        reverse=True,
    )
    return ordenadas[:top_k]


def recuperar_normas(consulta: str, top_k: int | None = None) -> list[NormaRecuperada]:
    """Igual que `recuperar`, pero devuelve modelos del dominio (NormaRecuperada).

    Es la forma que consumen los agentes Auditor y Verificador.
    """
    return [
        NormaRecuperada(
            tema=doc.metadata["tema"],
            fuente=doc.metadata["fuente"],
            texto=doc.page_content,
        )
        for doc in recuperar(consulta, top_k)
    ]
