"""S9 · Aspecto A-06 · ADR-0006: pesos, umbrales y semántica del resultado.

Estas pruebas fijan como decisión del equipo lo que un modelo (o una persona)
podría cambiar sin que ninguna otra prueba lo note.
"""
import pytest

from app.modules.analysis.analyzer import Finding, RuleAnalyzer
from app.modules.scoring.service import (
    MAX_SCORE,
    UMBRAL_RIESGO_ALTO,
    UMBRAL_RIESGO_MEDIO,
    calculate_score,
    classify_score,
)

TEXTO_CON_LAS_TRES_SENALES = (
    "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!!"
)


@pytest.mark.parametrize(
    ("score", "esperado"),
    [
        (0, "Riesgo bajo"),
        (29, "Riesgo bajo"),
        (30, "Riesgo medio"),
        (59, "Riesgo medio"),
        (60, "Riesgo alto"),
        (100, "Riesgo alto"),
    ],
)
def test_frontera_de_clasificacion(score: int, esperado: str) -> None:
    assert classify_score(score) == esperado


def test_umbrales_y_tope_son_los_declarados_en_adr_0006() -> None:
    assert (UMBRAL_RIESGO_MEDIO, UMBRAL_RIESGO_ALTO, MAX_SCORE) == (30, 60, 100)


def test_el_puntaje_se_limita_al_tope() -> None:
    hallazgos = [Finding("a", "a", 70), Finding("b", "b", 70)]

    assert calculate_score(hallazgos) == 100


def test_pesos_de_las_reglas_son_los_declarados_en_adr_0006() -> None:
    pesos = {
        f.indicator: f.points
        for f in RuleAnalyzer().analyze(TEXTO_CON_LAS_TRES_SENALES)
    }

    assert pesos == {
        "Lenguaje sensacionalista": 20,
        "Uso excesivo de mayúsculas": 15,
        "Afirmación absoluta": 15,
    }


def test_riesgo_alto_es_inalcanzable_con_las_reglas_actuales() -> None:
    """Límite conocido (ADR-0006): 20 + 15 + 15 = 50 < 60.

    Si agregas una regla y esta prueba falla, no la borres: revisa el ADR-0006
    y decide de forma explícita qué significa "Riesgo alto" con el nuevo máximo.
    """
    maximo = calculate_score(RuleAnalyzer().analyze(TEXTO_CON_LAS_TRES_SENALES))

    assert maximo == 50
    assert classify_score(maximo) != "Riesgo alto"


def test_limite_conocido_desinformacion_en_tono_neutro_no_genera_senales() -> None:
    """"Riesgo bajo" significa "sin señales de estilo", no "contenido confiable"."""
    texto = "El Ministerio confirmó que la vacuna causa esterilidad, según fuentes cercanas."

    hallazgos = RuleAnalyzer().analyze(texto)

    assert hallazgos == []
    assert classify_score(calculate_score(hallazgos)) == "Riesgo bajo"


def test_mismo_texto_produce_siempre_el_mismo_resultado() -> None:
    resultados = {
        (
            calculate_score(hallazgos := RuleAnalyzer().analyze(TEXTO_CON_LAS_TRES_SENALES)),
            tuple(f.indicator for f in hallazgos),
        )
        for _ in range(50)
    }

    assert len(resultados) == 1
