"""Demo de LexAudit — interfaz Streamlit.

Uso:  uv run streamlit run app.py
"""

import html
from pathlib import Path

import streamlit as st
from pypdf import PdfReader

from lexaudit.agents.redactor import DISCLAIMER
from lexaudit.graph.workflow import auditar_contrato
from lexaudit.models.schemas import Dictamen, Hallazgo, Reporte

EJEMPLOS = Path(__file__).parent / "examples"

# Color, ícono y etiqueta por tipo de dictamen.
_ESTILO: dict[Dictamen, tuple[str, str, str]] = {
    Dictamen.VIOLA: ("#d64545", "⛔", "Viola"),
    Dictamen.FALTANTE: ("#e08a3c", "⚠️", "Faltante"),
    Dictamen.AMBIGUA: ("#d4a72c", "❓", "Ambigua"),
    Dictamen.CUMPLE: ("#3c9a5f", "✅", "Cumple"),
    Dictamen.FUERA_DE_ALCANCE: ("#9aa0a6", "➖", "Fuera de alcance"),
}

_CSS = """
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding-top: 1.4rem; max-width: 1080px;}
  .lex-hero {
      background: linear-gradient(120deg, #1e3a5f 0%, #2f6db0 100%);
      color: #fff; padding: 26px 34px; border-radius: 14px;
  }
  .lex-hero h1 {margin: 0; font-size: 2rem;}
  .lex-hero p {margin: 6px 0 0; opacity: .92; font-size: .98rem;}
  .lex-card {
      border-left: 6px solid #9aa0a6; background: #f7f8fa;
      border-radius: 0 10px 10px 0; padding: 14px 20px; margin-bottom: 12px;
  }
  .lex-card h4 {margin: 0 0 8px; font-size: 1.02rem; color: #1e3a5f;}
  .lex-badge {
      display: inline-block; padding: 3px 12px; border-radius: 20px;
      color: #fff; font-size: .72rem; font-weight: 700; letter-spacing: .4px;
  }
  .lex-field {margin: 5px 0; font-size: .93rem; line-height: 1.5;}
  .lex-field b {color: #1e3a5f;}
  .lex-score {text-align: center; padding: 16px; border-radius: 14px; background: #eef2f6;}
  .lex-score .num {font-size: 3.1rem; font-weight: 800; line-height: 1;}
  .lex-score .lbl {font-size: .78rem; color: #5a6577; letter-spacing: 1px;}
</style>
"""


def _leer_pdf(archivo) -> str:
    """Extrae el texto de un PDF subido."""
    return "\n".join(p.extract_text() or "" for p in PdfReader(archivo).pages)


def _cargar_ejemplo() -> str:
    """Carga un contrato de ejemplo para precargar el área de texto."""
    ruta = EJEMPLOS / "contrato_ejemplo_1.txt"
    return ruta.read_text(encoding="utf-8") if ruta.exists() else ""


def _color_score(score: int) -> str:
    """Verde si el score es alto, amarillo si medio, rojo si bajo."""
    if score >= 80:
        return "#3c9a5f"
    if score >= 50:
        return "#d4a72c"
    return "#d64545"


def _tarjeta_hallazgo(h: Hallazgo) -> str:
    """Genera el HTML de una tarjeta de hallazgo."""
    color, icono, etiqueta = _ESTILO.get(
        h.dictamen, ("#9aa0a6", "•", h.dictamen.value)
    )
    partes = [
        f'<div class="lex-card" style="border-left-color:{color}">',
        f"<h4>{icono} Cláusula {h.clausula_id} — {h.tema.value}</h4>",
        f'<span class="lex-badge" style="background:{color}">{etiqueta}</span>',
        '<span class="lex-badge" style="background:#5a6577;margin-left:6px">'
        f"Severidad {h.severidad.value}</span>",
        '<div class="lex-field" style="margin-top:10px"><b>Análisis:</b> '
        f"{html.escape(h.explicacion)}</div>",
    ]
    if h.recomendacion:
        partes.append(
            '<div class="lex-field"><b>Recomendación:</b> '
            f"{html.escape(h.recomendacion)}</div>"
        )
    if h.normas_citadas:
        citas = ", ".join(html.escape(c) for c in h.normas_citadas)
        partes.append(f'<div class="lex-field"><b>Normas citadas:</b> {citas}</div>')
    if h.requiere_revision_humana:
        partes.append(
            '<div class="lex-field" style="color:#d64545">'
            "<b>⚠️ Requiere revisión humana.</b></div>"
        )
    partes.append("</div>")
    return "".join(partes)


def _mostrar_reporte(reporte: Reporte) -> None:
    """Renderiza el reporte de auditoría en pantalla."""
    st.markdown("### 📋 Reporte de auditoría")

    color = _color_score(reporte.score)
    izquierda, derecha = st.columns([1, 2.4])
    izquierda.markdown(
        f'<div class="lex-score"><div class="num" style="color:{color}">'
        f'{reporte.score}</div><div class="lbl">SCORE / 100</div></div>',
        unsafe_allow_html=True,
    )
    derecha.markdown(
        f"<br><b>Resumen.</b> {html.escape(reporte.resumen)}",
        unsafe_allow_html=True,
    )
    st.progress(reporte.score / 100)
    st.write("")

    for h in reporte.hallazgos:
        st.markdown(_tarjeta_hallazgo(h), unsafe_allow_html=True)

    st.caption(reporte.disclaimer)


def main() -> None:
    st.set_page_config(page_title="LexAudit", page_icon="⚖️", layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="lex-hero"><h1>⚖️ LexAudit</h1>'
        "<p>Auditor preliminar multiagente de riesgos en contratos laborales "
        "colombianos</p></div>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### ¿Cómo funciona?")
        st.markdown(
            "Un sistema **multiagente** orquestado con LangGraph audita el "
            "contrato cláusula por cláusula:"
        )
        st.markdown(
            "- **Segmentador** — divide el contrato\n"
            "- **Retriever (RAG)** — busca la norma aplicable\n"
            "- **Auditor** — dictamina la cláusula\n"
            "- **Verificador** — valida las citas\n"
            "- **Redactor** — consolida el reporte"
        )
        st.markdown("### Alcance")
        st.caption(
            "Salario mínimo · Jornada laboral · Período de prueba · "
            "Prestaciones sociales · Irrenunciabilidad de derechos"
        )

    st.info(f"ℹ️ {DISCLAIMER}")

    tab_texto, tab_archivo = st.tabs(["📝 Pegar texto", "📎 Subir archivo"])
    with tab_texto:
        texto = st.text_area(
            "Contrato laboral",
            value=_cargar_ejemplo(),
            height=260,
            label_visibility="collapsed",
        )
    with tab_archivo:
        archivo = st.file_uploader("Contrato (.txt o .pdf)", type=["txt", "pdf"])

    if st.button("🔍 Auditar contrato", type="primary", use_container_width=True):
        contenido = texto
        if archivo is not None:
            contenido = (
                _leer_pdf(archivo)
                if archivo.name.lower().endswith(".pdf")
                else archivo.read().decode("utf-8")
            )
        if not contenido.strip():
            st.error("No hay contrato para auditar.")
            return
        with st.spinner("Auditando el contrato... (unos segundos)"):
            reporte = auditar_contrato(contenido)
        _mostrar_reporte(reporte)


if __name__ == "__main__":
    main()
