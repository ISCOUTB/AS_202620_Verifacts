from app.modules.analysis.analyzer import Finding, RuleAnalyzer


def analyze_content(content: str) -> list[Finding]:
    analyzer = RuleAnalyzer()

    return analyzer.analyze(content)
