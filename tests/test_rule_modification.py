from app.modules.analysis.analyzer import RuleAnalyzer


def test_regla_modificada_detecta_nueva_palabra_absoluta() -> None:
    """
    Q-03 / A-02: valida que ampliar el conjunto de palabras absolutas de
    RuleAnalyzer es un cambio localizado a app/modules/analysis/analyzer.py
    y no rompe test_health.py ni test_analysis.py.
    """
    analyzer = RuleAnalyzer()

    findings = analyzer.analyze("Jamás debes confiar en esa fuente sin verificarla.")

    indicators = [finding.indicator for finding in findings]

    assert "Afirmación absoluta" in indicators
