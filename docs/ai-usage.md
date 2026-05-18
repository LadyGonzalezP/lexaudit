# Uso de IA en la construcción

Este documento registra cómo se usaron herramientas de inteligencia artificial durante la construcción de LexAudit. Su objetivo es evidenciar el uso deliberado, controlado y verificable de IA en el proceso de desarrollo.

## Herramienta utilizada

**Claude Code** — asistente de IA integrado en la terminal — se usó como par de programación durante el desarrollo del proyecto.

La IA no tomó decisiones finales de arquitectura ni de alcance. Fue utilizada como apoyo para acelerar análisis, generación de código, documentación y pruebas, manteniendo revisión humana en cada fase.

## Metodología: spec-driven development

No se programó únicamente mediante prompts sueltos o *vibe coding*. El flujo de trabajo fue guiado por una especificación previa:

1. **Spec primero.** Se redactó una especificación con requisitos, alcance, comportamiento esperado y criterios de aceptación (`docs/spec-lexaudit.md`) antes de implementar la solución.
2. **Plan por fases.** El trabajo se dividió en fases verificables: setup, corpus, RAG, agentes, grafo, demo y documentación.
3. **Construcción incremental.** Cada fase se implementó, probó y revisó antes de continuar con la siguiente.
4. **Validación humana.** Las salidas generadas por IA fueron revisadas y ajustadas antes de ser incorporadas al proyecto.

## Cómo se usó la IA por fase

| Fase | Uso de la IA |
|------|--------------|
| Diseño | Discusión de arquitectura, comparación de frameworks, definición del alcance y validación de trade-offs. |
| Corpus | Apoyo en la redacción inicial de fichas normativas, posteriormente revisadas contra fuentes legales aplicables. |
| Código | Generación asistida de componentes como agentes, RAG, modelos y grafo, siempre contra la especificación definida. |
| Tests | Apoyo en la generación de pruebas unitarias para lógica determinista y validaciones básicas. |
| Documentación | Apoyo en la redacción del README, documento de decisiones, guion de demo y explicación de arquitectura. |

## Criterio aplicado sobre las sugerencias

Las propuestas de la IA fueron evaluadas, no aceptadas automáticamente:

- Se **rechazó** usar proveedores de LLM de pago para mantener el presupuesto del proyecto en cero.
- Se **cambió de proveedor de LLM** durante el desarrollo: se empezó con Gemini, pero su free tier resultó muy limitado (20 solicitudes por día), por lo que se pasó a **Groq**. El cambio tocó un solo archivo — esto validó en la práctica el diseño provider-agnóstico del sistema.
- Se **mantuvo Gemini para los embeddings** del RAG, donde la cuota gratuita es suficiente.
- Se **verificaron manualmente** los datos legales incluidos en el corpus antes de usarlos como base del sistema.
- Se **acotó el alcance** a cinco temas laborales verificables cuando la idea inicial resultaba demasiado amplia para el tiempo disponible.
- Se **priorizó la trazabilidad** sobre la cobertura total, agregando un componente verificador determinista para reducir respuestas sin soporte normativo.

## Conclusión

La IA se utilizó como copiloto técnico y no como autoridad final. Las decisiones de alcance, arquitectura, validación y entrega fueron revisadas manualmente para asegurar coherencia con el reto, estabilidad de la demo y capacidad de sustentación.
