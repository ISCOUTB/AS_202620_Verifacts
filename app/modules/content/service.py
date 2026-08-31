def normalize_content(text: str) -> str:
    """
    Normaliza el contenido recibido antes del análisis.
    """

    normalized = " ".join(text.strip().split())

    if not normalized:
        raise ValueError("El contenido no puede estar vacío.")

    return normalized
