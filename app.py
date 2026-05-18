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

# Los 5 agentes (nombre, descripción) para el panel lateral.
_AGENTES = [
    ("Segmentador", "divide el contrato en cláusulas"),
    ("Retriever (RAG)", "busca la norma aplicable"),
    ("Auditor", "dictamina cada cláusula"),
    ("Verificador", "valida las citas"),
    ("Redactor", "consolida el reporte"),
]

# Los 5 temas auditables, para los chips del panel lateral.
_TEMAS = [
    "Salario mínimo",
    "Jornada laboral",
    "Período de prueba",
    "Prestaciones sociales",
    "Irrenunciabilidad",
]

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
  /* panel lateral */
  .lex-side-title {
      font-size: .8rem; font-weight: 700; color: #2f6db0;
      letter-spacing: 1px; text-transform: uppercase; margin: 4px 0 10px;
  }
  .lex-agente {display: flex; align-items: flex-start; gap: 10px; margin-bottom: 11px;}
  .lex-num {
      flex-shrink: 0; width: 25px; height: 25px; background: #2f6db0; color: #fff;
      border-radius: 50%; display: flex; align-items: center;
      justify-content: center; font-weight: 700; font-size: .8rem;
  }
  .lex-agente-txt {font-size: .9rem; line-height: 1.35;}
  .lex-agente-txt b {color: #1e3a5f;}
  .lex-agente-txt span {color: #5a6577; font-size: .83rem;}
  .lex-chip {
      display: inline-block; background: #e3ebf3; color: #1e3a5f;
      padding: 4px 11px; border-radius: 13px; font-size: .77rem;
      font-weight: 600; margin: 0 4px 6px 0;
  }
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


def _panel_lateral() -> None:
    """Dibuja el panel lateral: flujo de agentes y alcance."""
    with st.sidebar:
        st.markdown(
            '<div class="lex-side-title">⚙️ Cómo funciona</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Un sistema multiagente orquestado con LangGraph que audita el "
            "contrato cláusula por cláusula:"
        )
        agentes = "".join(
            f'<div class="lex-agente"><div class="lex-num">{i}</div>'
            f'<div class="lex-agente-txt"><b>{nombre}</b><br>'
            f"<span>{desc}</span></div></div>"
            for i, (nombre, desc) in enumerate(_AGENTES, start=1)
        )
        st.markdown(agentes, unsafe_allow_html=True)

        st.markdown(
            '<div class="lex-side-title" style="margin-top:18px">📋 Alcance</div>',
            unsafe_allow_html=True,
        )
        chips = "".join(f'<span class="lex-chip">{t}</span>' for t in _TEMAS)
        st.markdown(chips, unsafe_allow_html=True)


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

    _panel_lateral()

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
        try:
            with st.spinner("Auditando el contrato... (unos segundos)"):
                reporte = auditar_contrato(contenido)
        except Exception as error:  # noqa: BLE001 - en la UI capturamos todo
            st.error(
                "No se pudo completar la auditoría. El servicio de IA puede "
                "estar temporalmente saturado o no disponible. Espera unos "
                "segundos y vuelve a intentar."
            )
            st.caption(f"Detalle técnico: {type(error).__name__}")
            return
        _mostrar_reporte(reporte)


if __name__ == "__main__":
    main()
