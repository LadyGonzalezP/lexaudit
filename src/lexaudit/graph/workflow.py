"""Grafo de orquestación (LangGraph).

Este es el "director": invoca a cada agente en orden y transporta los datos
entre ellos. El contrato se procesa cláusula por cláusula. El grafo tiene tres
puntos de decisión (edges condicionales):

1. Tras segmentar: si no hay cláusulas, va directo a redactar.
2. Tras verificar: si el hallazgo no se verificó y quedan intentos, reaudita
   (loop); si no, avanza.
3. Tras avanzar: si quedan cláusulas, procesa la siguiente; si no, redacta.
"""

from langgraph.graph import END, START, StateGraph

from lexaudit.agents.auditor import auditar
from lexaudit.agents.redactor import redactar
from lexaudit.agents.segmentador import segmentar
from lexaudit.agents.verificador import verificar
from lexaudit.config import settings
from lexaudit.graph.state import EstadoAuditoria
from lexaudit.models.schemas import Reporte
from lexaudit.rag.retriever import recuperar_normas

# --------------------------------------------------------------------------
# Nodos: cada uno recibe el estado, hace su trabajo y devuelve los cambios.
# --------------------------------------------------------------------------


def nodo_segmentar(estado: EstadoAuditoria) -> dict:
    """Divide el contrato en cláusulas e inicializa el recorrido."""
    clausulas = segmentar(estado["contrato"])
    return {"clausulas": clausulas, "indice": 0, "hallazgos": []}


def nodo_recuperar(estado: EstadoAuditoria) -> dict:
    """Recupera (RAG) las normas aplicables a la cláusula en proceso."""
    clausula = estado["clausulas"][estado["indice"]]
    return {"normas_actuales": recuperar_normas(clausula.texto), "intentos": 0}


def nodo_auditar(estado: EstadoAuditoria) -> dict:
    """El Auditor dictamina la cláusula en proceso."""
    clausula = estado["clausulas"][estado["indice"]]
    hallazgo = auditar(clausula, estado["normas_actuales"])
    return {"hallazgo_actual": hallazgo, "intentos": estado["intentos"] + 1}


def nodo_verificar(estado: EstadoAuditoria) -> dict:
    """El Verificador comprueba que el hallazgo tenga citas válidas."""
    hallazgo = verificar(estado["hallazgo_actual"], estado["normas_actuales"])
    return {"hallazgo_actual": hallazgo}


def nodo_avanzar(estado: EstadoAuditoria) -> dict:
    """Finaliza la cláusula actual y pasa a la siguiente."""
    hallazgo = estado["hallazgo_actual"]
    # Si tras los reintentos no se verificó, se deriva a revisión humana.
    if not hallazgo.verificado:
        hallazgo.requiere_revision_humana = True
    hallazgo.intentos = estado["intentos"]
    return {
        "hallazgos": estado["hallazgos"] + [hallazgo],
        "indice": estado["indice"] + 1,
        "hallazgo_actual": None,
    }


def nodo_redactar(estado: EstadoAuditoria) -> dict:
    """El Redactor consolida todos los hallazgos en el reporte final."""
    return {"reporte": redactar(estado["hallazgos"])}


# --------------------------------------------------------------------------
# Decisiones: funciones que deciden a qué nodo ir (edges condicionales).
# --------------------------------------------------------------------------


def decidir_tras_segmentar(estado: EstadoAuditoria) -> str:
    """Si el contrato no tiene cláusulas, va directo a redactar."""
    return "recuperar" if estado["clausulas"] else "redactar"


def decidir_tras_verificar(estado: EstadoAuditoria) -> str:
    """Si el hallazgo no se verificó y quedan intentos, reaudita (loop)."""
    hallazgo = estado["hallazgo_actual"]
    if not hallazgo.verificado and estado["intentos"] < settings.max_reintentos_verificacion:
        return "auditar"
    return "avanzar"


def decidir_tras_avanzar(estado: EstadoAuditoria) -> str:
    """Si quedan cláusulas por procesar, sigue; si no, redacta."""
    if estado["indice"] < len(estado["clausulas"]):
        return "recuperar"
    return "redactar"


# --------------------------------------------------------------------------
# Construcción del grafo.
# --------------------------------------------------------------------------


def construir_grafo():
    """Arma y compila el grafo de auditoría."""
    g = StateGraph(EstadoAuditoria)

    g.add_node("segmentar", nodo_segmentar)
    g.add_node("recuperar", nodo_recuperar)
    g.add_node("auditar", nodo_auditar)
    g.add_node("verificar", nodo_verificar)
    g.add_node("avanzar", nodo_avanzar)
    g.add_node("redactar", nodo_redactar)

    g.add_edge(START, "segmentar")
    g.add_conditional_edges(
        "segmentar", decidir_tras_segmentar,
        {"recuperar": "recuperar", "redactar": "redactar"},
    )
    g.add_edge("recuperar", "auditar")
    g.add_edge("auditar", "verificar")
    g.add_conditional_edges(
        "verificar", decidir_tras_verificar,
        {"auditar": "auditar", "avanzar": "avanzar"},
    )
    g.add_conditional_edges(
        "avanzar", decidir_tras_avanzar,
        {"recuperar": "recuperar", "redactar": "redactar"},
    )
    g.add_edge("redactar", END)

    return g.compile()


# El grafo se compila una sola vez, al importar el módulo (no en cada petición).
_GRAFO = construir_grafo()


def auditar_contrato(texto_contrato: str) -> Reporte:
    """Punto de entrada: audita un contrato completo y devuelve el reporte."""
    estado_final = _GRAFO.invoke(
        {"contrato": texto_contrato},
        config={"recursion_limit": 100},
    )
    return estado_final["reporte"]
