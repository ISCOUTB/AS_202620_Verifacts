# Restricciones arquitectónicas — VeriFacts

| ID | Restricción | Clasificación | Justificación | Impacto arquitectónico |
|---|---|---|---|---|
| R-ORG-01 | Desarrollo durante un semestre | Organizativa | Tiempo académico limitado | Reduce complejidad de infraestructura |
| R-ORG-02 | Equipo pequeño | Organizativa | Capacidad limitada | Favorece monolito modular |
| R-ORG-03 | Alcance académico | Organizativa | Se busca demostrar arquitectura y prototipo | Evita infraestructura productiva innecesaria |
| R-TEC-01 | Ejecución local | Técnica | No se exige despliegue productivo | Permite infraestructura mínima |
| R-TEC-02 | Recursos computacionales limitados | Técnica | No existe infraestructura especializada | Limita complejidad de modelos y procesamiento |
| R-TEC-03 | Tecnologías disponibles | Técnica | Reduce curva de aprendizaje | Python, FastAPI, React |
| R-TEC-04 | Persistencia sencilla | Técnica | Prototipo local | SQLite inicialmente |
| R-LEG-01 | No presentar el resultado como verdad absoluta | Legal / alcance | El análisis no sustituye verificación humana | Resultado expresado como riesgo |
| R-LEG-02 | Evitar datos sensibles innecesarios | Legal / organizativa | Reducir exposición durante el desarrollo | Persistencia mínima |
