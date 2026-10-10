"""Reescribe serverless-prototype/events/analysis_event.json con el payload de 10.000 caracteres.

Uso (desde la raíz del repo):  python scripts/generar_evento_sam.py
"""
import json
from pathlib import Path

from payload_10k import payload_10k

RUTA = Path("serverless-prototype/events/analysis_event.json")

evento = json.loads(RUTA.read_text(encoding="utf-8"))

if "body" not in evento:
    raise SystemExit(
        "El evento no tiene la clave 'body'. Abre el JSON y ajusta este script "
        "a la clave donde va el texto."
    )

evento["body"] = json.dumps({"text": payload_10k()}, ensure_ascii=False)
RUTA.write_text(json.dumps(evento, ensure_ascii=False, indent=2), encoding="utf-8")
print("Evento actualizado. Caracteres del texto:", len(payload_10k()))
