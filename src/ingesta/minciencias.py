"""
ingesta/minciencias.py
======================
Descarga las convocatorias de investigadores reconocidos de Minciencias
desde el portal de Datos Abiertos de Colombia (datos.gov.co) usando la
librería sodapy y guarda los resultados como archivos CSV en datos/raw/.

Uso directo:
    python -m src.ingesta.minciencias

Uso como función:
    from src.ingesta.minciencias import descargar_convocatorias
    descargar_convocatorias()
"""

import logging
import os
from pathlib import Path

import pandas as pd
from sodapy import Socrata

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parámetros Socrata
# ---------------------------------------------------------------------------

# Dominio del portal de Datos Abiertos Colombia
SOCRATA_DOMAIN = "www.datos.gov.co"

# App token opcional (None = acceso sin autenticación, límite de peticiones más bajo).
# Para uso intensivo, registrar una app en https://www.datos.gov.co y pasar el token
# mediante la variable de entorno SOCRATA_APP_TOKEN.
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", None)

# IDs de los datasets de Investigadores Reconocidos por Convocatoria
CONVOCATORIAS = {
    "2017": "bqtm-4y2h",
    "2019": "izwp-q8gg",
    "2021": "gzff-pwwc",
}

# Directorio de destino para los archivos descargados
RUTA_RAW = Path(__file__).resolve().parents[2] / "datos" / "raw"


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def descargar_convocatorias(
    convocatorias: dict = None,
    ruta_destino: Path = None,
    dominio: str = SOCRATA_DOMAIN,
    app_token: str = None,
) -> dict:
    """Descarga las convocatorias desde datos.gov.co y las guarda como CSV.

    Parameters
    ----------
    convocatorias : dict, optional
        Mapeo ``{año: dataset_id}`` de los datasets a descargar.
        Por defecto usa ``CONVOCATORIAS``.
    ruta_destino : Path, optional
        Carpeta donde se guardarán los archivos CSV.
        Por defecto usa ``datos/raw/`` relativa a la raíz del proyecto.
    dominio : str, optional
        Dominio Socrata. Por defecto ``"www.datos.gov.co"``.
    app_token : str, optional
        App token de Socrata. Si es ``None`` se usa ``SOCRATA_APP_TOKEN``
        (variable de entorno o acceso anónimo).

    Returns
    -------
    dict
        Mapeo ``{año: Path}`` con las rutas de los archivos descargados.
    """
    if convocatorias is None:
        convocatorias = CONVOCATORIAS
    if ruta_destino is None:
        ruta_destino = RUTA_RAW
    if app_token is None:
        app_token = SOCRATA_APP_TOKEN

    ruta_destino = Path(ruta_destino)
    ruta_destino.mkdir(parents=True, exist_ok=True)

    client = Socrata(dominio, app_token, timeout=60)
    archivos = {}

    try:
        for anio, dataset_id in convocatorias.items():
            logger.info(
                "Descargando convocatoria %s (dataset_id=%s) …", anio, dataset_id
            )
            try:
                registros = client.get_all(dataset_id)
                df = pd.DataFrame.from_records(registros)
            except Exception as exc:
                logger.error(
                    "Error al descargar convocatoria %s (dataset_id=%s): %s",
                    anio,
                    dataset_id,
                    exc,
                )
                raise

            logger.info(
                "  → %d registros obtenidos para la convocatoria %s.", len(df), anio
            )

            nombre_archivo = f"investigadores_reconocidos_{anio}.csv"
            ruta_archivo = ruta_destino / nombre_archivo
            df.to_csv(ruta_archivo, index=False, encoding="utf-8-sig")
            logger.info("  → Guardado en %s", ruta_archivo)
            archivos[anio] = ruta_archivo
    finally:
        client.close()

    logger.info("Descarga completada. Archivos guardados en %s", ruta_destino)
    return archivos


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    descargar_convocatorias()
