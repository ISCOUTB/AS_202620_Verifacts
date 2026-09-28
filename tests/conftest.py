"""Aísla la base de datos de las pruebas: nunca escriben en data/verifacts.db.

El repositorio lee VERIFACTS_DATA_DIR al importarse, por eso la variable se fija
aquí, antes de que cualquier prueba importe `app`.
"""
import atexit
import os
import shutil
import tempfile

_TEST_DATA_DIR = tempfile.mkdtemp(prefix="verifacts-tests-")
os.environ["VERIFACTS_DATA_DIR"] = _TEST_DATA_DIR
atexit.register(shutil.rmtree, _TEST_DATA_DIR, ignore_errors=True)
