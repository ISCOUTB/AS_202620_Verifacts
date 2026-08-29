# arc42 — Sección 4: Estrategia de solución

## 4.1 Estilo arquitectónico

VeriFacts utilizará un **monolito modular** como estilo arquitectónico
principal.

La aplicación se ejecutará como una única unidad, pero estará organizada
internamente mediante módulos con responsabilidades claramente delimitadas.

Los módulos principales son:

- API.
- Content.
- Analysis.
- Scoring.

---

## 4.2 Razón de la decisión

El monolito modular permite mantener una ejecución sencilla y adecuada para
un proyecto académico, mientras proporciona límites internos que facilitan
la evolución de los mecanismos de análisis.

La decisión responde principalmente a los escenarios de:

- Escalabilidad.
- Mantenibilidad.
- Rendimiento.
- Confiabilidad.

---

## 4.3 Tácticas

### Q-01 — Rendimiento

Los módulos compartirán el mismo proceso, evitando inicialmente llamadas de
red entre componentes internos.

### Q-02 — Escalabilidad

Los mecanismos de análisis se mantendrán separados para permitir incorporar
nuevas reglas y futuros analizadores.

### Q-03 — Mantenibilidad

Se utilizarán responsabilidades separadas, alta cohesión y bajo acoplamiento.


### Q-04 — Usabilidad

Se priorizará una salida estructurada (puntuación, clasificación, factores) en
lenguaje simple, evitando terminología técnica de NLP/ML en la respuesta al
usuario final.

### Q-05 — Confiabilidad

Se utilizarán pruebas automatizadas para verificar las rutas y componentes
principales.

---

## 4.4 Evolución

La arquitectura inicial no utiliza microservicios.

Si durante el desarrollo un componente presenta necesidades independientes de
escala, procesamiento o despliegue, se evaluará posteriormente si resulta
justificado separarlo.

Esta evolución no forma parte del alcance actual.
