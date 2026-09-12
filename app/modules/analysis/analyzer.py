from dataclasses import dataclass


@dataclass
class Finding:
    indicator: str
    description: str
    points: int


class RuleAnalyzer:
    """
    Analizador determinista basado en reglas simples.
    """

    def analyze(self, content: str) -> list[Finding]:
        findings: list[Finding] = []

        if "!!!" in content:
            findings.append(
                Finding(
                    indicator="Lenguaje sensacionalista",
                    description="El contenido utiliza múltiples signos de exclamación.",
                    points=20,
                )
            )

        uppercase_words = [
            word for word in content.split()
            if len(word) >= 4 and word.isupper()
        ]

        if uppercase_words:
            findings.append(
                Finding(
                    indicator="Uso excesivo de mayúsculas",
                    description="Se detectaron palabras escritas completamente en mayúsculas.",
                    points=15,
                )
            )

               absolute_words = {
            "siempre",
            "nunca",
            "todos",
            "nadie",
            "100%",
            "jamás",
        }

        content_words = {
            word.strip(".,;:!?¿¡()[]{}").lower()
            for word in content.split()
        }

        detected_absolute_words = absolute_words.intersection(content_words)

        if detected_absolute_words:
            findings.append(
                Finding(
                    indicator="Afirmación absoluta",
                    description="El contenido contiene expresiones absolutas.",
                    points=15,
                )
            )

        return findings
