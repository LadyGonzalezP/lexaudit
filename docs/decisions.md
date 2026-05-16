# Documento de decisiones — LexAudit

## El problema

En Colombia, las PyMEs y los emprendedores redactan contratos laborales sin
asesoría legal —un abogado es caro— y firman cláusulas que incumplen la ley
sin saberlo: salarios por debajo del mínimo, jornadas excesivas, períodos de
prueba ilegales, renuncias a derechos irrenunciables. Esto deriva en multas y
demandas laborales. LexAudit hace una **auditoría preliminar automática**:
detecta esos riesgos y los reporta con su fundamento normativo y un score.

## Por qué este diseño

**Sistema multiagente, no un prompt único.** Auditar un contrato son tareas
distintas —segmentar, recuperar la norma, dictaminar, verificar, redactar—.
Cada agente tiene una responsabilidad única; eso hace el sistema testeable,
explicable y extensible.

**Orquestación con LangGraph.** El reto pide orquestación explícita. LangGraph
modela el flujo como un grafo de estados con loops y decisiones: el flujo *es*
el código, y el diagrama de arquitectura se deriva directo de él.

**RAG sobre un corpus curado.** El conocimiento legal no se "clava" en los
prompts: vive en 5 fichas Markdown que el RAG recupera con búsqueda híbrida
(vectorial + BM25). Agregar un tema es agregar una ficha, sin tocar agentes.

**Verificador determinista.** El agente Verificador comprueba —en código, no
con un LLM— que cada cita exista en lo recuperado. No se pone una IA a vigilar
a otra IA: la verificación de pertenencia es una operación exacta.

**Provider-agnóstico.** El acceso al LLM está aislado en una sola capa.
Durante el desarrollo se cambió de Gemini a Groq por un límite de cuota: tocó
un archivo, ningún agente.

## Trade-offs (qué se sacrificó)

- **Alcance acotado a 5 temas.** Se sacrificó cobertura por verificabilidad y
  una demo estable. Auditar 5 temas bien supera a auditar 50 mal; la
  arquitectura escala agregando fichas al corpus.
- **Procesamiento secuencial de cláusulas.** Un fan-out paralelo sería más
  rápido, pero se priorizó la simplicidad y el respeto a los límites de tasa
  del proveedor de LLM.
- **Solo PDFs digitales.** Los PDF escaneados requerirían una etapa de OCR;
  queda como extensión futura.
- **Verificación de citas, no de fundamento jurídico.** El Verificador
  comprueba que la norma citada exista, no que el razonamiento sea
  jurídicamente perfecto. Por eso el sistema es *preliminar* — y lo declara.
