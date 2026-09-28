from app.modules.analysis.service import Finding

# Decisión del equipo, registrada en docs/adr/0006-semantica-del-resultado.md.
# No cambiar estos valores sin actualizar el ADR y tests/test_scoring_boundaries.py
# en el mismo commit (lo haya escrito una persona o una IA).
MAX_SCORE = 100
UMBRAL_RIESGO_MEDIO = 30  # score < 30  -> "Riesgo bajo"
UMBRAL_RIESGO_ALTO = 60   # score < 60  -> "Riesgo medio"; score >= 60 -> "Riesgo alto"


def calculate_score(findings: list[Finding]) -> int:
    score = sum(finding.points for finding in findings)

    return min(score, MAX_SCORE)


def classify_score(score: int) -> str:
    if score < UMBRAL_RIESGO_MEDIO:
        return "Riesgo bajo"

    if score < UMBRAL_RIESGO_ALTO:
        return "Riesgo medio"

    return "Riesgo alto"
