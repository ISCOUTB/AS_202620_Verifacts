# 9. aspectos

Aquí tenemos que crear **la tabla de 8 columnas** y enlazar los escenarios.

# Aspecto arquitectónico — VeriFacts

## Aspecto seleccionado

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

---

## Matriz del aspecto y sus escenarios

| ID | Aspecto | Atributo | Preocupación | Escenario | Medida | Impacto | Riesgo |
|---|---|---|---|---|---|---|---|
| A-01 | Escalabilidad | Escalabilidad | Incorporar nuevos mecanismos de análisis | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Cambio limitado al módulo Analysis y sus pruebas | Alto | Alto |
| A-02 | Escalabilidad | Mantenibilidad | Modificar reglas existentes | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Cambio localizado sin regresiones | Alto | Medio-alto |

---

## Decisión

La arquitectura utilizará un monolito modular.

Los módulos `API`, `Content`, `Analysis` y `Scoring` tendrán responsabilidades
separadas para evitar que la incorporación de nuevos mecanismos de análisis
genere modificaciones transversales.

---

## Relación con la decisión arquitectónica

El escenario Q-02 es el principal escenario que justifica la selección del
monolito modular.

La decisión no se basa en que el monolito modular sea universalmente superior,
sino en que permite alcanzar la evolución gradual requerida por VeriFacts sin
introducir la complejidad operativa de una arquitectura distribuida.

Esto corrige directamente el árbol que el profesor llamó "lista plana".

---

# 11. `docs/aspectos.md`

Necesitas exactamente **8 columnas**.

Pon:

```markdown
# Aspectos arquitectónicos — VeriFacts

## Aspecto principal

El aspecto arquitectónico principal seleccionado es:

**Escalabilidad mediante modularidad.**

La arquitectura debe permitir incorporar nuevos mecanismos de análisis sin
modificar significativamente los demás componentes.

## Matriz de trazabilidad

| ID | Aspecto | Atributo | Preocupación | Escenario | Medida | Impacto | Riesgo |
|---|---|---|---|---|---|---|---|
| A-01 | Escalabilidad | Escalabilidad | Incorporar nuevos mecanismos | [Q-02](escenarios-de-calidad.md#q-02--incorporación-de-un-nuevo-analizador) | Cambio limitado a Analysis y sus pruebas | Alto | Alto |
| A-02 | Escalabilidad | Mantenibilidad | Modificar reglas existentes | [Q-03](escenarios-de-calidad.md#q-03--modificación-de-una-regla) | Cambio localizado sin regresiones | Alto | Medio-alto |

## Decisión relacionada

La decisión arquitectónica se encuentra registrada en:

[ADR-0001 — Usar monolito modular](adr/0001-estilo-arquitectonico.md)

## Relación

El escenario Q-02 es el escenario principal que motiva la selección del
monolito modular.

El escenario Q-03 complementa la decisión al exigir cambios localizados en
las reglas de análisis.

Las tácticas concretas que responden a estos escenarios están documentadas en:

[arc42 sección 4](arc42/04-estrategia-de-solucion.md)
