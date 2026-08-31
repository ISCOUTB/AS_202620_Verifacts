from app.modules.analysis.analyzer import Finding


def calculate_score(findings: list[Finding]) -> int:
    score = sum(finding.points for finding in findings)

    return min(score, 100)


def classify_score(score: int) -> str:
    if score < 30:
        return "Riesgo bajo"

    if score < 60:
        return "Riesgo medio"

    return "Riesgo alto"
