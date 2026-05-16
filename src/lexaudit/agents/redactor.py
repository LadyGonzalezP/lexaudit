"""Agente Redactor.

Consolida todos los hallazgos en el Reporte final: los ordena por severidad,
calcula un score de cumplimiento y redacta un resumen.

No usa LLM: contar hallazgos y calcular un puntaje son operaciones
deterministas, y un resumen por plantilla es predecible y reproducible para
la demo en vivo.
"""

from lexaudit.models.schemas import Dictamen, Hallazgo, Reporte, Severidad

DISCLAIMER = (
    "Este sistema no reemplaza asesoría legal profesional. Genera una revisión "
    "preliminar basada en un corpus normativo curado."
)

# Puntos que descuenta del score cada hallazgo, según dictamen y severidad.
_DESCUENTOS: dict[tuple[Dictamen, Severidad], int] = {
    (Dictamen.VIOLA, Severidad.ALTA): 25,
    (Dictamen.VIOLA, Severidad.MEDIA): 15,
    (Dictamen.VIOLA, Severidad.BAJA): 10,
    (Dictamen.FALTANTE, Severidad.ALTA): 10,
    (Dictamen.FALTANTE, Severidad.MEDIA): 10,
    (Dictamen.FALTANTE, Severidad.BAJA): 10,
    (Dictamen.AMBIGUA, Severidad.ALTA): 5,
    (Dictamen.AMBIGUA, Severidad.MEDIA): 5,
    (Dictamen.AMBIGUA, Severidad.BAJA): 5,
}

_ORDEN_SEVERIDAD = {Severidad.ALTA: 0, Severidad.MEDIA: 1, Severidad.BAJA: 2}


def _calcular_score(hallazgos: list[Hallazgo]) -> int:
    """Score de cumplimiento: arranca en 100 y descuenta por cada hallazgo."""
    descuento = sum(_DESCUENTOS.get((h.dictamen, h.severidad), 0) for h in hallazgos)
    return max(0, 100 - descuento)


def _generar_resumen(hallazgos: list[Hallazgo]) -> str:
    """Resumen textual del reporte (plantilla determinista)."""
    violaciones = sum(1 for h in hallazgos if h.dictamen == Dictamen.VIOLA)
    faltantes = sum(1 for h in hallazgos if h.dictamen == Dictamen.FALTANTE)
    ambiguas = sum(1 for h in hallazgos if h.dictamen == Dictamen.AMBIGUA)
    revision = sum(1 for h in hallazgos if h.requiere_revision_humana)

    partes = [
        f"Se auditaron {len(hallazgos)} cláusulas.",
        f"Violaciones detectadas: {violaciones}.",
        f"Cláusulas obligatorias ausentes: {faltantes}.",
        f"Cláusulas ambiguas: {ambiguas}.",
    ]
    if revision:
        partes.append(f"{revision} hallazgo(s) requieren revisión humana.")
    return " ".join(partes)


def redactar(hallazgos: list[Hallazgo]) -> Reporte:
    """Consolida los hallazgos en el reporte final, priorizados por severidad."""
    ordenados = sorted(
        hallazgos,
        key=lambda h: (
            _ORDEN_SEVERIDAD.get(h.severidad, 9),
            h.dictamen != Dictamen.VIOLA,  # dentro de una severidad, VIOLA primero
        ),
    )
    return Reporte(
        hallazgos=ordenados,
        score=_calcular_score(hallazgos),
        resumen=_generar_resumen(hallazgos),
        disclaimer=DISCLAIMER,
    )
