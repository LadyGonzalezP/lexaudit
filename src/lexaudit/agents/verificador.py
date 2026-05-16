"""Agente Verificador.

Comprueba que cada hallazgo del Auditor esté respaldado: que las normas que
cita existan realmente entre las que el RAG recuperó.

Es una verificación DETERMINISTA, hecha en código y no con un LLM, a propósito:
usar un modelo para verificar a otro modelo agregaría una segunda fuente de
alucinación. Comprobar que una cita pertenece a un conjunto es una operación
exacta, sin ambigüedad.
"""

from lexaudit.models.schemas import Dictamen, Hallazgo, NormaRecuperada

# Dictámenes que no se fundamentan en una norma citada: no requieren verificación.
_SIN_VERIFICACION = {Dictamen.FUERA_DE_ALCANCE, Dictamen.FALTANTE}


def verificar(hallazgo: Hallazgo, normas: list[NormaRecuperada]) -> Hallazgo:
    """Marca el hallazgo como verificado si sus citas son válidas.

    Un hallazgo es válido cuando cita al menos una norma y todas las normas
    citadas están entre las recuperadas por el RAG. Si no, queda sin verificar:
    el grafo decidirá si reintentar la auditoría o derivar a revisión humana.
    """
    if hallazgo.dictamen in _SIN_VERIFICACION:
        hallazgo.verificado = True
        return hallazgo

    fuentes_disponibles = {n.fuente for n in normas}
    citas_invalidas = [
        cita for cita in hallazgo.normas_citadas if cita not in fuentes_disponibles
    ]

    # Verificado solo si cita al menos una norma y ninguna cita es inventada.
    hallazgo.verificado = bool(hallazgo.normas_citadas) and not citas_invalidas
    return hallazgo
