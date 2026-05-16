"""Estado compartido del grafo de auditoría.

En LangGraph, el "estado" es un objeto que fluye por todos los nodos: cada
nodo lo lee, devuelve cambios, y esos cambios se fusionan en el estado. Este
TypedDict define qué campos tiene ese estado a lo largo del recorrido.
"""

from typing import TypedDict

from lexaudit.models.schemas import Clausula, Hallazgo, NormaRecuperada, Reporte


class EstadoAuditoria(TypedDict, total=False):
    """Estado que recorre el grafo. `total=False`: los campos se van llenando."""

    contrato: str                           # texto del contrato (entrada)
    clausulas: list[Clausula]               # cláusulas segmentadas
    indice: int                             # índice de la cláusula en proceso
    normas_actuales: list[NormaRecuperada]  # normas recuperadas para esa cláusula
    hallazgo_actual: Hallazgo | None        # hallazgo en curso (puede reintentarse)
    intentos: int                           # reintentos de auditoría de la cláusula
    hallazgos: list[Hallazgo]               # hallazgos ya finalizados
    reporte: Reporte | None                 # reporte final (salida)
