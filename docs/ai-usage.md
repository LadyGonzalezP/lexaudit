# Uso de IA en la construcción

Este documento registra cómo se usaron herramientas de IA para construir
LexAudit, según pide el reto.

## Herramienta

**Claude Code** — un asistente de IA que opera en la terminal — se usó como
par de programación durante todo el desarrollo.

## Metodología: spec-driven development

No se programó "por prompts sueltos" (*vibe coding*). El flujo fue:

1. **Spec primero.** Se redactó una especificación con requisitos y criterios
   de aceptación (`docs/spec-lexaudit.md`) antes de escribir una línea de código.
2. **Plan por fases.** El trabajo se dividió en fases verificables: setup,
   corpus, RAG, agentes, grafo, demo, documentación.
3. **Construcción incremental.** Cada fase se escribió, se probó y se verificó
   antes de avanzar. Nada se daba por terminado sin evidencia (un test que
   pasa, una corrida correcta).

## Cómo se usó la IA, por fase

| Fase | Uso de la IA |
|------|--------------|
| Diseño | Discusión de arquitectura, comparación de frameworks, definición del alcance |
| Corpus | Redacción de las fichas normativas (verificadas después contra el Código Sustantivo del Trabajo) |
| Código | Generación de los agentes, el RAG y el grafo, escritos contra la spec |
| Depuración | Diagnóstico de errores reales (modelo no disponible, cuota agotada) y su resolución |
| Tests | Generación de la suite unitaria de la lógica determinista |
| Documentación | Redacción del README, los diagramas y este documento |

## Qué decidió la persona, no la IA

La IA asistió; las decisiones fueron propias:

- El problema a resolver y el recorte del alcance a 5 temas.
- La elección de framework (LangGraph) y de proveedor (Groq).
- La verificación de los datos legales contra fuentes oficiales.
- La aceptación o el rechazo de cada sugerencia de la IA.

## Criterio aplicado sobre las sugerencias

Las propuestas de la IA se evaluaron, no se aceptaron a ciegas:

- Se **rechazó** usar un proveedor de LLM de pago, para mantener el
  presupuesto en cero.
- Se **verificó en fuente oficial** un dato legal (el salario mínimo) que la
  IA había reportado con una advertencia de duda.
- Se **acotó el alcance** cuando una idea inicial resultaba demasiado
  ambiciosa para el plazo de entrega.
