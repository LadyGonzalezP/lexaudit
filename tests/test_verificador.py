"""Tests del agente Verificador.

El Verificador es determinista (no usa LLM), así que se testea unitariamente.
"""

from lexaudit.agents.verificador import verificar
from lexaudit.models.schemas import Dictamen, Hallazgo, NormaRecuperada, Severidad, Tema

_NORMAS = [
    NormaRecuperada(tema="SALARIO_MINIMO", fuente="salario_minimo.md", texto="...")
]


def _hallazgo(dictamen: Dictamen, normas_citadas: list[str]) -> Hallazgo:
    """Construye un hallazgo de prueba."""
    return Hallazgo(
        clausula_id=1,
        tema=Tema.SALARIO_MINIMO,
        dictamen=dictamen,
        severidad=Severidad.ALTA,
        explicacion="texto de prueba",
        normas_citadas=normas_citadas,
    )


def test_cita_valida_se_verifica() -> None:
    hallazgo = verificar(_hallazgo(Dictamen.VIOLA, ["salario_minimo.md"]), _NORMAS)
    assert hallazgo.verificado is True


def test_cita_inventada_se_rechaza() -> None:
    hallazgo = verificar(_hallazgo(Dictamen.VIOLA, ["norma_inexistente.md"]), _NORMAS)
    assert hallazgo.verificado is False


def test_sin_citas_se_rechaza() -> None:
    hallazgo = verificar(_hallazgo(Dictamen.VIOLA, []), _NORMAS)
    assert hallazgo.verificado is False


def test_fuera_de_alcance_no_requiere_verificacion() -> None:
    hallazgo = verificar(_hallazgo(Dictamen.FUERA_DE_ALCANCE, []), _NORMAS)
    assert hallazgo.verificado is True


def test_faltante_no_requiere_verificacion() -> None:
    hallazgo = verificar(_hallazgo(Dictamen.FALTANTE, []), _NORMAS)
    assert hallazgo.verificado is True
