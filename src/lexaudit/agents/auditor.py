"""Agente Auditor.

Recibe una cláusula y las normas que el RAG recuperó para ella, y emite un
dictamen (un Hallazgo). Dos casos se resuelven sin llamar al LLM:

- Cláusulas FUERA_DE_ALCANCE: no se auditan (el sistema declara su límite).
- Cláusulas ausentes: el dictamen es FALTANTE de forma directa.

Resolverlos en código —y no con el modelo— ahorra llamadas y hace el
comportamiento predecible.
"""

from pydantic import BaseModel

from lexaudit.config import settings
from lexaudit.llm.provider import get_llm
from lexaudit.models.schemas import (
    Clausula,
    Dictamen,
    Hallazgo,
    NormaRecuperada,
    Severidad,
    Tema,
)
from lexaudit.prompts.auditor import PROMPT_AUDITOR


class _SalidaAuditor(BaseModel):
    """Forma de salida que se le exige al LLM."""

    dictamen: Dictamen
    severidad: Severidad
    explicacion: str
    normas_citadas: list[str]
    recomendacion: str = ""


def _formatear_normas(normas: list[NormaRecuperada]) -> str:
    """Arma el bloque de normas para el prompt, cada una con su nombre de archivo."""
    return "\n\n".join(f"### Ficha: {n.fuente}\n{n.texto}" for n in normas)


def auditar(clausula: Clausula, normas: list[NormaRecuperada]) -> Hallazgo:
    """Emite un dictamen sobre una cláusula frente a las normas recuperadas."""
    # Caso 1: fuera de alcance — el sistema no audita este tema.
    if clausula.tema == Tema.FUERA_DE_ALCANCE:
        return Hallazgo(
            clausula_id=clausula.id,
            tema=clausula.tema,
            dictamen=Dictamen.FUERA_DE_ALCANCE,
            severidad=Severidad.BAJA,
            explicacion="Cláusula fuera del alcance de esta auditoría preliminar.",
        )

    # Caso 2: cláusula obligatoria ausente.
    if clausula.es_ausencia:
        return Hallazgo(
            clausula_id=clausula.id,
            tema=clausula.tema,
            dictamen=Dictamen.FALTANTE,
            severidad=Severidad.ALTA,
            explicacion="El contrato no contiene una cláusula obligatoria sobre este tema.",
            recomendacion=f"Incluir una cláusula que regule {clausula.tema.value}.",
        )

    # Caso 3: el LLM dictamina contra las normas recuperadas por el RAG.
    llm = get_llm().with_structured_output(_SalidaAuditor)
    salida: _SalidaAuditor = llm.invoke(
        PROMPT_AUDITOR.format(
            clausula=clausula.texto,
            normas=_formatear_normas(normas),
            smmlv=f"{settings.smmlv:,}",
            jornada=settings.jornada_max_semanal,
        )
    )
    return Hallazgo(
        clausula_id=clausula.id,
        tema=clausula.tema,
        dictamen=salida.dictamen,
        severidad=salida.severidad,
        explicacion=salida.explicacion,
        normas_citadas=salida.normas_citadas,
        recomendacion=salida.recomendacion,
    )
