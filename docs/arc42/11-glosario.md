# arc42 — Sección 12: Glosario

| Término | Definición |
|---|---|
| **Análisis (Analysis)** | Bloque arquitectónico responsable de aplicar los mecanismos de detección de indicadores de desinformación sobre un contenido normalizado. |
| **Analizador (Analyzer)** | Contrato/interfaz común que implementará cada mecanismo de análisis (`RuleAnalyzer`, `NLPAnalyzer`, `MLAnalyzer`), permitiendo incorporar nuevos sin modificar los demás módulos. |
| **Clasificación** | Categoría resultante del análisis de un contenido (por ejemplo, nivel de riesgo), derivada de la puntuación. |
| **Contenido (Content)** | Bloque arquitectónico responsable de representar y procesar el texto o la URL introducidos por el usuario. |
| **Corte vertical (vertical slice)** | Recorrido mínimo y ejecutable de extremo a extremo del sistema. En este incremento existen dos: `GET /health` (solo `API`) y `POST /analysis` (`API → Content → Analysis → Scoring → Persistencia`). |
| **Escenario de calidad** | Descripción estructurada (fuente, estímulo, artefacto, entorno, respuesta, medida) de un requisito de calidad verificable, identificado como Q-01…Q-05. |
| **Indicador** | Señal detectada en el contenido (por ejemplo, lenguaje sensacionalista o ausencia de fuentes) que contribuye a la puntuación de riesgo. |
| **Monolito modular** | Estilo arquitectónico seleccionado (ver ADR-0001): la aplicación se despliega como una única unidad, pero está organizada internamente en módulos con responsabilidades delimitadas. |
| **Puntuación (Scoring)** | Bloque arquitectónico responsable de transformar los hallazgos del análisis en un valor numérico de riesgo, una clasificación y una explicación. |
| **Regla** | Mecanismo de análisis determinista y explicable (por ejemplo, detectar exceso de mayúsculas o afirmaciones absolutas), primera estrategia de detección adoptada por el proyecto. |
| **Persistencia** | Bloque arquitectónico responsable de almacenar y recuperar los resultados de los análisis; implementado con SQLite (`app/persistence/repository.py`). |
| **ADR (Architecture Decision Record)** | Documento que registra una decisión arquitectónica significativa, su contexto, alternativas consideradas y consecuencias. |
| **arc42** | Plantilla utilizada para documentar la arquitectura de VeriFacts, organizada en 12 secciones estándar. |
| **C4** | Modelo de diagramación arquitectónica en niveles (Contexto, Contenedores, Componentes, Código) utilizado para representar VeriFacts gráficamente. |
| **P95** | Percentil 95 de una distribución de mediciones (por ejemplo, tiempo de respuesta); métrica usada en el escenario Q-01. |
|**Contenido**|texto o URL que el usuario envía para analizar.|
|**Análisis**|proceso que evalúa un Contenido en busca de señales de desinformación.|
|**Factor / Señal**|indicio individual detectado por el motor de reglas o el motor NLP.|
|**Puntuación (Score)**|valor numérico resultante de combinar las Señales de un Análisis.|
|**Clasificación**|etiqueta derivada de la Puntuación.|
|**Historial**|registro persistente de Análisis pasados.|*Este glosario se ampliará en incrementos posteriores conforme se incorporen nuevos términos del dominio (por ejemplo, terminología específica de NLP/ML cuando se implemente esa parte del módulo `Analysis`).*
