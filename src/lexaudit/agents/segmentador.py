"""Agente Segmentador.

Primer agente del pipeline. Hace dos cosas:
1. Divide el texto del contrato en cláusulas y clasifica cada una por tema.
2. Detecta ausencias: temas obligatorios que el contrato no aborda.

El LLM solo clasifica lo que ve; la detección de ausencias la hace el código
(compara los temas presentes contra los obligatorios). Así el límite del
sistema es explícito y no depende del criterio del modelo.
"""

from pydantic import BaseModel

from lexaudit.llm.provider import get_llm
from lexaudit.models.schemas import Clausula, Tema
from lexaudit.prompts.segmentador import PROMPT_SEGMENTADOR

# Temas que un contrato laboral debe abordar de forma explícita.
_TEMAS_OBLIGATORIOS = {Tema.SALARIO_MINIMO, Tema.JORNADA_LABORAL}


class _ClausulaDetectada(BaseModel):
    """Forma de salida que se le pide al LLM por cada cláusula."""

    texto: str
    tema: Tema


class _SalidaSegmentador(BaseModel):
    """Estructura completa que el LLM debe devolver."""

    clausulas: list[_ClausulaDetectada]


def segmentar(texto_contrato: str) -> list[Clausula]:
    """Divide el contrato en cláusulas y agrega marcadores de ausencia."""
    # with_structured_output obliga al LLM a responder con la forma exacta:
    # no devuelve texto libre que haya que parsear, devuelve el objeto tipado.
    llm = get_llm().with_structured_output(_SalidaSegmentador)
    salida: _SalidaSegmentador = llm.invoke(
        PROMPT_SEGMENTADOR.format(contrato=texto_contrato)
    )

    clausulas = [
        Clausula(id=i, texto=c.texto, tema=c.tema)
        for i, c in enumerate(salida.clausulas, start=1)
    ]

    # Ausencias: temas obligatorios que no aparecen en ninguna cláusula.
    temas_presentes = {c.tema for c in clausulas}
    siguiente_id = len(clausulas) + 1
    for tema in _TEMAS_OBLIGATORIOS - temas_presentes:
        clausulas.append(
            Clausula(
                id=siguiente_id,
                texto=f"(El contrato no contiene una cláusula sobre {tema.value}.)",
                tema=tema,
                es_ausencia=True,
            )
        )
        siguiente_id += 1

    return clausulas
