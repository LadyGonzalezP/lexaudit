"""Tests del agente Redactor.

El Redactor es determinista (score y resumen por fórmula), se testea unitario.
"""

from lexaudit.agents.redactor import redactar
from lexaudit.models.schemas import Dictamen, Hallazgo, Severidad, Tema


def _hallazgo(dictamen: Dictamen, severidad: Severidad) -> Hallazgo:
    """Construye un hallazgo de prueba."""
    return Hallazgo(
        clausula_id=1,
        tema=Tema.SALARIO_MINIMO,
        dictamen=dictamen,
        severidad=severidad,
        explicacion="texto de prueba",
    )


def test_score_sin_hallazgos_es_100() -> None:
    assert redactar([]).score == 100


def test_score_descuenta_por_violacion_alta() -> None:
    reporte = redactar([_hallazgo(Dictamen.VIOLA, Severidad.ALTA)])
    assert reporte.score == 75  # 100 - 25


def test_score_no_baja_de_cero() -> None:
    hallazgos = [_hallazgo(Dictamen.VIOLA, Severidad.ALTA) for _ in range(10)]
    assert redactar(hallazgos).score == 0


def test_reporte_incluye_disclaimer() -> None:
    assert "asesoría legal" in redactar([]).disclaimer


def test_hallazgos_ordenados_por_severidad() -> None:
    baja = _hallazgo(Dictamen.VIOLA, Severidad.BAJA)
    alta = _hallazgo(Dictamen.VIOLA, Severidad.ALTA)
    reporte = redactar([baja, alta])
    assert reporte.hallazgos[0].severidad == Severidad.ALTA
