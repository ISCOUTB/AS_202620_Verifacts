"""Piezas simuladas: reloj manual (sin `sleep`) y fetcher con guion de fallos."""
from __future__ import annotations


class ManualClock:
    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def now(self) -> float:
        return self._now

    def advance_to(self, instant: float) -> None:
        self._now = max(self._now, instant)


class TransientFetchError(Exception):
    """Fallo recuperable: timeout, 5xx, conexión rechazada."""


class PermanentFetchError(Exception):
    """Fallo no recuperable: 404, 403 anti-bot, contenido ilegible."""


class ScriptedFetcher:
    """Simula `extract_from_url`: por URL, una lista de resultados en orden.

    Cada elemento es un texto (éxito) o una excepción (fallo). Cuando el guion
    se agota, repite el último elemento.
    """

    def __init__(self, script: dict[str, list]) -> None:
        self._script = {url: list(steps) for url, steps in script.items()}
        self.calls: dict[str, int] = {}

    def __call__(self, url: str) -> str:
        steps = self._script[url]
        index = self.calls.get(url, 0)
        self.calls[url] = index + 1
        step = steps[min(index, len(steps) - 1)]
        if isinstance(step, Exception):
            raise step
        return step
