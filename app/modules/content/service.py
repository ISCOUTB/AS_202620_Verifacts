import trafilatura


def normalize_content(text: str) -> str:
    """
    Normaliza el contenido recibido antes del análisis.
    """

    normalized = " ".join(text.strip().split())

    if not normalized:
        raise ValueError("El contenido no puede estar vacío.")

    return normalized


def extract_from_url(url: str) -> str:
    """


    downloaded = trafilatura.fetch_url(url)

    if downloaded is None:
        raise ValueError(
            f"No se pudo descargar el contenido de la URL: {url}"
        )

    extracted = trafilatura.extract(downloaded)

    if not extracted or not extracted.strip():
        raise ValueError(
            f"No se pudo extraer contenido legible de la URL: {url}"
        )

    return extracted
