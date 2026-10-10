"""Payload común de 10.000 caracteres para Render, local y SAM (escenario Q-01)."""

BASE = "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla. "


def payload_10k() -> str:
    texto = (BASE * (10_000 // len(BASE) + 1))[:10_000]
    assert len(texto) == 10_000
    return texto
