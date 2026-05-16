# SPEC — LexAudit

> Especificación funcional del MVP. Define QUÉ debe hacer el sistema y CÓMO
> sabemos que está listo. Es la base del código.
> Concepto general: ver `idea-final-reto-seti.md`.

---

## 1. Resumen

LexAudit es un sistema multiagente que recibe un contrato laboral colombiano y
produce un reporte de auditoría preliminar: hallazgos priorizados, cada uno con
cita a la norma, recomendación de corrección y un score de cumplimiento.

---

## 2. Objetivo del MVP

Demostrar un sistema multiagente con orquestación explícita, RAG y verificación
anti-alucinación, sobre un alcance acotado y verificable.

---

## 3. Alcance

**Dentro:**
- 5 temas: salario mínimo, jornada laboral, período de prueba, prestaciones
  sociales, irrenunciabilidad de derechos.
- Contratos laborales individuales (término fijo, indefinido, obra/labor).
- Jurisdicción Colombia (Código Sustantivo del Trabajo).
- Idioma español. Input en PDF o texto.

**Fuera (escalabilidad futura, se menciona en la sustentación):**
- Otros temas laborales. Otras jurisdicciones. Otros tipos de contrato.
- Asesoría legal vinculante. Multi-idioma.

---

## 4. Requisitos funcionales

| ID | Requisito |
|----|-----------|
| RF-1 | El sistema acepta un contrato laboral como PDF o texto plano |
| RF-2 | Segmenta el contrato en cláusulas individuales |
| RF-3 | Detecta cláusulas obligatorias ausentes (cargo, salario, jornada…) |
| RF-4 | Por cada cláusula, recupera del corpus las normas aplicables (RAG) |
| RF-5 | Dictamina cada cláusula: CUMPLE / VIOLA / AMBIGUA / FALTANTE / FUERA_DE_ALCANCE |
| RF-6 | Verifica que cada dictamen cite una norma presente en lo recuperado |
| RF-7 | Si la verificación falla, reintenta (máx. 2); luego marca "requiere revisión humana" |
| RF-8 | Genera un reporte: hallazgos priorizados por severidad + recomendaciones + score |
| RF-9 | El reporte y el README muestran el disclaimer de no-asesoría-legal |
| RF-10 | El sistema se ejecuta en vivo mediante una app Streamlit |

---

## 5. Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF-1 | Costo $0 — solo Gemini free tier, sin OpenAI/Azure |
| RNF-2 | El RAG corre offline (embeddings locales) — no depende de quota de API |
| RNF-3 | Reproducible — dependencias fijadas, instrucciones en README |
| RNF-4 | Salida estable — temperatura baja en los agentes para una demo consistente |
| RNF-5 | Código tipado (Pydantic) y verificado (ruff) |
| RNF-6 | Una auditoría de un contrato de ejemplo termina en tiempo razonable (~minutos) |

---

## 6. Los agentes — contrato de cada uno

| Agente | Recibe | Devuelve | Responsabilidad |
|--------|--------|----------|-----------------|
| **Segmentador** | Texto del contrato | Lista de `Clausula` + lista de obligatorias ausentes | Partir y clasificar por tema; detectar ausencias |
| **Retriever** | Una `Clausula` | Lista de `NormaRecuperada` | Recuperación híbrida sobre el corpus |
| **Auditor** | `Clausula` + normas | `Hallazgo` (sin verificar) | Dictaminar con explicación y citas |
| **Verificador** | `Hallazgo` + normas | `Hallazgo` (verificado o rechazado) | Comprobar que las citas existan en lo recuperado |
| **Redactor** | Lista de `Hallazgo` | `Reporte` | Consolidar, priorizar, recomendar, calcular score |

---

## 7. Modelo de datos (Pydantic)

```
Tema (enum): SALARIO_MINIMO | JORNADA_LABORAL | PERIODO_PRUEBA |
             PRESTACIONES_SOCIALES | IRRENUNCIABILIDAD | FUERA_DE_ALCANCE

Dictamen (enum): CUMPLE | VIOLA | AMBIGUA | FALTANTE | FUERA_DE_ALCANCE
Severidad (enum): ALTA | MEDIA | BAJA

Clausula:        id, texto, tema, es_ausencia (bool)
NormaRecuperada: ficha_id, titulo, articulo, texto, fuente
Hallazgo:        clausula_id, tema, dictamen, severidad, explicacion,
                 normas_citadas (list), recomendacion, verificado (bool),
                 requiere_revision_humana (bool)
Reporte:         hallazgos (list), score (int 0-100), resumen, disclaimer
```

---

## 8. El corpus

5 fichas Markdown en `corpus/`, una por tema. Cada ficha:
título · artículo/norma · texto resumido · fuente · regla verificable ·
ejemplo de incumplimiento.

---

## 9. Cálculo del score (versión MVP, ajustable)

Score inicia en 100. Cada hallazgo descuenta:
- VIOLA severidad ALTA → −25
- VIOLA severidad MEDIA → −15
- FALTANTE → −10
- AMBIGUA → −5

Score final = máx(0, 100 − descuentos). Se documenta como heurística simple.

---

## 10. Casos límite y manejo de errores

| Caso | Comportamiento esperado |
|------|-------------------------|
| Contrato vacío o PDF ilegible | Mensaje de error claro, sin crash |
| Cláusula que no corresponde a ningún tema | Dictamen FUERA_DE_ALCANCE — nunca se ignora en silencio |
| Verificador rechaza 2 veces | Hallazgo marcado `requiere_revision_humana`, sin loop infinito |
| Corpus no indexado | El sistema avisa que debe correrse el ingest primero |

---

## 11. Criterios de aceptación

| ID | Criterio (verificable) |
|----|------------------------|
| CA-1 | Dado un contrato con salario por debajo del mínimo, el reporte incluye un hallazgo VIOLA del tema SALARIO_MINIMO citando la norma correspondiente |
| CA-2 | Dado un contrato sin cláusula de salario, el reporte incluye un hallazgo FALTANTE |
| CA-3 | Dado un dictamen que cita una norma inexistente en lo recuperado, el Verificador lo rechaza |
| CA-4 | Dada una cláusula sobre un tema fuera de los 5, el dictamen es FUERA_DE_ALCANCE |
| CA-5 | El reporte final incluye score (0-100) y disclaimer |
| CA-6 | La app Streamlit recibe un contrato y muestra el reporte sin intervención manual |
| CA-7 | El sistema corre de punta a punta sin claves de pago (solo Gemini free) |

---

## 12. Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Corpus mal curado → recuperación pobre | Fichas curadas a mano, estructura fija, revisadas |
| LLM alucina una norma | Agente Verificador la rechaza |
| Demo inestable en vivo | Temperatura baja + contratos de ejemplo probados de antemano |
| Quota de Gemini agotada | Embeddings locales; contratos de ejemplo cacheados |

---

## 13. Definición de "terminado"

El MVP está listo cuando los 7 criterios de aceptación pasan y la demo
Streamlit corre de punta a punta con los contratos de ejemplo.
