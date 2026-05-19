# Idea final — Reto Técnico Ingeniero IA · SETI S.A.S

> **ESTADO: DECISIÓN FINAL — CERRADA.** Este documento describe la solución
> acordada. No está en discusión. Para el detalle de implementación ver el
> documento hermano `spec-lexaudit.md`.
> Versión 3 — con calendario y deadline confirmado.

---

## 0. Resumen ejecutivo (lectura de 30 segundos)

- **Qué:** LexAudit — sistema multiagente que audita contratos laborales
  colombianos y produce un reporte de riesgos con citas y score.
- **Framework:** LangGraph (orquestación por grafo de estados explícito).
- **LLM:** proveedor configurable mediante capa `llm/provider.py`.
- **Proveedor usado en demo:** Groq.
- **Decisión:** arquitectura provider-agnostic para poder cambiar entre Gemini, Groq u otro proveedor sin modificar agentes ni grafo.
- **Agentes (5):** Segmentador, Retriever, Auditor, Verificador, Redactor.
- **Orquestación:** grafo con fan-out por cláusula + loop de verificación.
- **RAG:** corpus curado de 5 fichas Markdown + recuperación híbrida + ChromaDB.
- **Alcance:** 5 temas laborales verificables (no todo el derecho laboral).
- **Demo:** Streamlit.
- **Decisión clave / trade-off:** alcance acotado a 5 temas para garantizar
  verificabilidad y una demo estable. Escalar = agregar fichas al corpus.

---

## 1. El problema

En LATAM, las PyMEs y los emprendedores redactan contratos laborales **sin
asesoría legal** porque un abogado laboral es caro. Resultado: contratos con
cláusulas que incumplen la ley sin que nadie lo note (salario por debajo del
mínimo, jornada excesiva, período de prueba ilegal, cláusulas nulas, ausencia
de cláusulas obligatorias). Esto deriva en multas, demandas y litigios.

**Valor:** el sistema entrega en minutos una auditoría preliminar que un
abogado cobra caro y tarda horas. Democratiza una primera revisión.

---

## 2. La solución

Un **sistema multiagente** que recibe un contrato laboral y produce un
**reporte de auditoría preliminar**: hallazgos priorizados por severidad, cada
uno con **cita a la norma exacta**, **recomendación de corrección** y un
**score de cumplimiento (0-100)**.

No está diseñado como chatbot conversacional general. Su objetivo principal es producir un entregable estructurado: un reporte de auditoría preliminar.

No estoy intentando auditar todo el derecho laboral colombiano. Estoy demostrando una arquitectura escalable con cinco temas verificables

- **Input:** un contrato laboral (PDF o texto).
- **Output:** un reporte de auditoría estructurado, con citas, recomendaciones
  y score.

**Disclaimer (va siempre, en README y en el reporte):**
> Este sistema no reemplaza asesoría legal profesional. Genera una revisión
> preliminar basada en un corpus normativo curado.

---

## 3. Alcance MVP — 5 temas verificables

1. **Salario mínimo** — el salario pactado vs. el SMMLV vigente.
2. **Jornada laboral** — horas pactadas vs. el máximo legal.
3. **Período de prueba** — duración pactada vs. la permitida.
4. **Prestaciones sociales** — que el contrato no las excluya ni desconozca.
5. **Cláusulas nulas / irrenunciabilidad de derechos.**

**Trade-off (se documenta y se defiende):** se sacrifica cobertura por
profundidad y confiabilidad. La arquitectura permite escalar agregando fichas
al corpus, sin reescribir agentes.

---

## 4. Los agentes (5 roles diferenciados)

| # | Agente | Rol |
|---|--------|-----|
| 1 | **Segmentador** | Parte el contrato en cláusulas y detecta cláusulas obligatorias ausentes |
| 2 | **Retriever (RAG)** | Para cada cláusula, recupera del corpus las normas aplicables |
| 3 | **Auditor** | Dictamina por cláusula: CUMPLE / VIOLA / AMBIGUA / FALTANTE / FUERA_DE_ALCANCE |
| 4 | **Verificador** | Anti-alucinación: comprueba que cada dictamen cite una norma real recuperada. Si no → rechaza y devuelve al Auditor |
| 5 | **Redactor** | Consolida el reporte: hallazgos priorizados + recomendaciones + score |

---

## 5. La orquestación (LangGraph)

```
              ┌──────────────┐
   Contrato → │ Segmentador  │
              └──────┬───────┘
                     │  fan-out: una rama por cláusula
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ┌─────────────────────────────────┐
     │ Retriever → Auditor → Verificador│ ◄─┐ loop si el
     └────────────────┬────────────────┘   │ Verificador
                      │ ✔ verificado       │ rechaza
                      │                ────┘
                      ▼
             ┌──────────────────┐
             │     Redactor     │ → Reporte + Score
             └──────────────────┘
```

Patrones: **map / fan-out** (subflujo por cláusula) · **loop condicional**
(verificación) · **manejo de errores** (tras N rechazos → revisión humana).

---

## 6. RAG y corpus

Corpus curado — un Markdown por tema en `corpus/`:
`salario_minimo.md`, `jornada_laboral.md`, `periodo_prueba.md`,
`prestaciones_sociales.md`, `irrenunciabilidad_derechos.md`.

Cada ficha: título · artículo/norma · texto resumido · fuente ·
regla verificable · ejemplo de incumplimiento.

Recuperación híbrida (vectorial + BM25) · ChromaDB local ·
embeddings sentence-transformers locales (sin quota, demo offline).

---

## 7. Stack técnico (todo gratuito)

| Capa | Herramienta |
|------|-------------|
| Lenguaje | Python 3.12 |
| Orquestación | LangGraph + LangChain |
| LLM | Google Gemini (`langchain-google-genai`) — free tier | Groq 
| Embeddings | sentence-transformers (local) |
| Vector store | ChromaDB (local) |
| Lectura de PDF | pypdf |
| Schemas / estado | Pydantic |
| Demo / frontend | Streamlit |
| Calidad de código | ruff + pytest |
| Gestión de deps | uv (con `requirements.txt` para el evaluador) |

**Regla dura: NO se usa OpenAI ni Azure OpenAI** — tienen costo. Gemini o Groq

---

## 8. Estructura del repositorio

```
lexaudit/
├── README.md                  # instalación + ejecución + disclaimer
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── app.py                     # entrada Streamlit (la demo en vivo)
│
├── src/lexaudit/
│   ├── config.py
│   ├── agents/
│   │   ├── segmentador.py
│   │   ├── auditor.py
│   │   ├── verificador.py
│   │   └── redactor.py
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── vectorstore.py
│   ├── models/
│   │   └── schemas.py
│   ├── prompts/
│   └── llm/
│       └── provider.py
│
├── corpus/                    # 5 fichas Markdown
├── data/chroma/               # vector store persistido (gitignored)
├── examples/                  # contratos de ejemplo para la demo
├── tests/
└── docs/
    ├── decisions.md           # documento de decisiones (entregable)
    ├── ai-usage.md            # diario de uso de IA
    └── architecture-diagram.png  # diagrama (entregable)
```

---

## 9. Cómo cubre los criterios del reto (20% c/u)

| Criterio | Cómo se cubre |
|---|---|
| Problema y solución | Problema claro, valor trazable, alcance acotado y justificado |
| Arquitectura | 5 roles diferenciados + map + loop + manejo de errores |
| Calidad de código | Estructura modular, ruff, pytest, separación de responsabilidades |
| Uso de IA en el proceso | `docs/ai-usage.md` — diario real, no solo discurso |

---

## 11. Supuestos (todos confirmados)

- [x] Framework: LangGraph.
- [x] Jurisdicción: Colombia (Código Sustantivo del Trabajo).
- [x] Solo contratos laborales individuales.
- [x] Idioma: español.