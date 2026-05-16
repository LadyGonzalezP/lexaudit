"""Tests de las funciones de decisión del grafo.

Las decisiones del grafo (a qué nodo ir) son deterministas: se testean unitario.
"""

from lexaudit.graph.workflow import (
    decidir_tras_avanzar,
    decidir_tras_segmentar,
    decidir_tras_verificar,
)
from lexaudit.models.schemas import Clausula, Dictamen, Hallazgo, Severidad, Tema


def _clausula() -> Clausula:
    return Clausula(id=1, texto="texto", tema=Tema.SALARIO_MINIMO)


def _hallazgo(verificado: bool) -> Hallazgo:
    return Hallazgo(
        clausula_id=1,
        tema=Tema.SALARIO_MINIMO,
        dictamen=Dictamen.VIOLA,
        severidad=Severidad.ALTA,
        explicacion="texto",
        verificado=verificado,
    )


def test_sin_clausulas_va_a_redactar() -> None:
    assert decidir_tras_segmentar({"clausulas": []}) == "redactar"


def test_con_clausulas_va_a_recuperar() -> None:
    assert decidir_tras_segmentar({"clausulas": [_clausula()]}) == "recuperar"


def test_no_verificado_con_intentos_disponibles_reaudita() -> None:
    estado = {"hallazgo_actual": _hallazgo(False), "intentos": 1}
    assert decidir_tras_verificar(estado) == "auditar"


def test_hallazgo_verificado_avanza() -> None:
    estado = {"hallazgo_actual": _hallazgo(True), "intentos": 1}
    assert decidir_tras_verificar(estado) == "avanzar"


def test_intentos_agotados_avanza() -> None:
    estado = {"hallazgo_actual": _hallazgo(False), "intentos": 2}
    assert decidir_tras_verificar(estado) == "avanzar"


def test_quedan_clausulas_recupera_la_siguiente() -> None:
    estado = {"indice": 1, "clausulas": [_clausula(), _clausula(), _clausula()]}
    assert decidir_tras_avanzar(estado) == "recuperar"


def test_todas_las_clausulas_procesadas_redacta() -> None:
    estado = {"indice": 3, "clausulas": [_clausula(), _clausula(), _clausula()]}
    assert decidir_tras_avanzar(estado) == "redactar"
