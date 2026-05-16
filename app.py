"""Demo de LexAudit — interfaz Streamlit.

Uso:  uv run streamlit run app.py
"""

from pathlib import Path

import streamlit as st
from pypdf import PdfReader

from lexaudit.agents.redactor import DISCLAIMER
from lexaudit.graph.workflow import auditar_contrato
from lexaudit.models.schemas import Dictamen, Reporte

EJEMPLOS = Path(__file__).parent / "examples"

# Ícono por tipo de dictamen, para el reporte visual.
_ICONO = {
    Dictamen.VIOLA: "🔴",
    Dictamen.FALTANTE: "🟠",
    Dictamen.AMBIGUA: "🟡",
    Dictamen.CUMPLE: "🟢",
    Dictamen.FUERA_DE_ALCANCE: "⚪",
}


def _leer_pdf(archivo) -> str:
    """Extrae el texto de un PDF subido."""
    lector = PdfReader(archivo)
    return "\n".join(pagina.extract_text() or "" for pagina in lector.pages)


def _cargar_ejemplo() -> str:
    """Carga un contrato de ejemplo para precargar el área de texto."""
    ruta = EJEMPLOS / "contrato_ejemplo_1.txt"
    return ruta.read_text(encoding="utf-8") if ruta.exists() else ""


def _mostrar_reporte(reporte: Reporte) -> None:
    """Renderiza el reporte de auditoría en pantalla."""
    st.divider()
    st.subheader("📋 Reporte de auditoría")

    izquierda, derecha = st.columns([1, 3])
    izquierda.metric("Score de cumplimiento", f"{reporte.score} / 100")
    derecha.write(reporte.resumen)

    for h in reporte.hallazgos:
        icono = _ICONO.get(h.dictamen, "•")
        titulo = f"{icono} {h.dictamen.value} — {h.tema.value} (cláusula {h.clausula_id})"
        with st.expander(titulo, expanded=h.dictamen == Dictamen.VIOLA):
            st.markdown(f"**Severidad:** {h.severidad.value}")
            st.markdown(f"**Análisis:** {h.explicacion}")
            if h.recomendacion:
                st.markdown(f"**Recomendación:** {h.recomendacion}")
            if h.normas_citadas:
                st.markdown(f"**Normas citadas:** {', '.join(h.normas_citadas)}")
            if h.requiere_revision_humana:
                st.warning("⚠️ Este hallazgo requiere revisión humana.")

    st.caption(reporte.disclaimer)


def main() -> None:
    st.set_page_config(page_title="LexAudit", page_icon="⚖️", layout="wide")
    st.title("⚖️ LexAudit")
    st.caption(
        "Auditor preliminar multiagente de riesgos en contratos laborales colombianos"
    )
    st.info(f"ℹ️ {DISCLAIMER}")

    archivo = st.file_uploader("Subí un contrato (.txt o .pdf)", type=["txt", "pdf"])
    texto = st.text_area(
        "...o pegá el texto del contrato",
        value=_cargar_ejemplo(),
        height=280,
    )

    if st.button("Auditar contrato", type="primary"):
        if archivo is not None:
            texto = (
                _leer_pdf(archivo)
                if archivo.name.lower().endswith(".pdf")
                else archivo.read().decode("utf-8")
            )
        if not texto.strip():
            st.error("No hay contrato para auditar.")
            return
        with st.spinner("Auditando el contrato... (esto toma unos segundos)"):
            reporte = auditar_contrato(texto)
        _mostrar_reporte(reporte)


if __name__ == "__main__":
    main()
