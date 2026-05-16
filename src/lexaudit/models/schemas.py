"""Modelos de datos del dominio (Pydantic).

Estas son las "formas" que viajan por el sistema. Una Clausula entra al
pipeline, el Auditor produce un Hallazgo sobre ella, y el Redactor consolida
todos los hallazgos en un Reporte. Usar modelos tipados (en vez de
diccionarios sueltos) hace que un error de forma se detecte de inmediato.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class Tema(StrEnum):
    """Los 5 temas auditables + el marcador de lo que queda fuera de alcance."""

    SALARIO_MINIMO = "SALARIO_MINIMO"
    JORNADA_LABORAL = "JORNADA_LABORAL"
    PERIODO_PRUEBA = "PERIODO_PRUEBA"
    PRESTACIONES_SOCIALES = "PRESTACIONES_SOCIALES"
    IRRENUNCIABILIDAD = "IRRENUNCIABILIDAD"
    FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"


class Dictamen(StrEnum):
    """Veredicto del Auditor sobre una cláusula."""

    CUMPLE = "CUMPLE"
    VIOLA = "VIOLA"
    AMBIGUA = "AMBIGUA"
    FALTANTE = "FALTANTE"
    FUERA_DE_ALCANCE = "FUERA_DE_ALCANCE"


class Severidad(StrEnum):
    """Gravedad de un hallazgo, para priorizar el reporte."""

    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class Clausula(BaseModel):
    """Un fragmento del contrato, clasificado por tema."""

    id: int
    texto: str
    tema: Tema
    es_ausencia: bool = False  # True = cláusula obligatoria que falta en el contrato


class NormaRecuperada(BaseModel):
    """Una ficha del corpus recuperada por el RAG."""

    tema: str
    fuente: str  # nombre del archivo de la ficha (p. ej. "salario_minimo.md")
    texto: str


class Hallazgo(BaseModel):
    """El dictamen del Auditor sobre una cláusula, con su evidencia."""

    clausula_id: int
    tema: Tema
    dictamen: Dictamen
    severidad: Severidad
    explicacion: str
    normas_citadas: list[str] = Field(default_factory=list)  # fuentes citadas
    recomendacion: str = ""
    verificado: bool = False
    requiere_revision_humana: bool = False
    intentos: int = 0


class Reporte(BaseModel):
    """El entregable final: todos los hallazgos consolidados."""

    hallazgos: list[Hallazgo]
    score: int
    resumen: str
    disclaimer: str
