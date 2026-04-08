# -*- coding: utf-8 -*-
"""
ingesta.py

Módulo de ingesta de datos para el Observatorio de Ciencia, Tecnología e
Innovación — Investigadores Reconocidos Minciencias (Grupo 7).

Lee los archivos de las convocatorias 2017, 2019 y 2021 desde la carpeta de
datos y los combina en un único DataFrame consolidado que se guarda en
datos/tarea_join/.
"""

import pathlib
import pandas as pd

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "datos" / "tarea_join"

ARCHIVO_CONSOLIDADO_CSV = DATA_DIR / "investigadores_consolidado.csv"
ARCHIVO_CONSOLIDADO_XLSX = DATA_DIR / "investigadores_consolidado.xlsx"


# ---------------------------------------------------------------------------
# Funciones de lectura
# ---------------------------------------------------------------------------

def cargar_csv(ruta: pathlib.Path, **kwargs) -> pd.DataFrame:
    """Lee un archivo CSV y devuelve un DataFrame."""
    return pd.read_csv(ruta, **kwargs)


def cargar_excel(ruta: pathlib.Path, **kwargs) -> pd.DataFrame:
    """Lee un archivo Excel (.xlsx) y devuelve un DataFrame."""
    return pd.read_excel(ruta, **kwargs)


def cargar_consolidado() -> pd.DataFrame:
    """
    Carga el archivo consolidado de investigadores.

    Intenta primero el CSV; si no existe, usa el XLSX.

    Returns
    -------
    pd.DataFrame
        DataFrame con todos los registros de las convocatorias.
    """
    if ARCHIVO_CONSOLIDADO_CSV.exists():
        print(f"[ingesta] Cargando CSV: {ARCHIVO_CONSOLIDADO_CSV}")
        df = cargar_csv(ARCHIVO_CONSOLIDADO_CSV, low_memory=False)
    elif ARCHIVO_CONSOLIDADO_XLSX.exists():
        print(f"[ingesta] Cargando XLSX: {ARCHIVO_CONSOLIDADO_XLSX}")
        df = cargar_excel(ARCHIVO_CONSOLIDADO_XLSX)
    else:
        raise FileNotFoundError(
            "No se encontró el archivo consolidado en "
            f"{DATA_DIR}. Ejecute primero notebooks/tarea_join/codigo_join.py."
        )
    print(f"[ingesta] Registros cargados: {len(df):,}  |  Columnas: {df.shape[1]}")
    return df


def consolidar_fuentes(rutas: list[pathlib.Path]) -> pd.DataFrame:
    """
    Concatena múltiples archivos CSV/XLSX en un único DataFrame.

    Parameters
    ----------
    rutas : list[pathlib.Path]
        Lista de rutas a los archivos de cada convocatoria.

    Returns
    -------
    pd.DataFrame
        DataFrame consolidado con todos los registros.
    """
    frames = []
    for ruta in rutas:
        ruta = pathlib.Path(ruta)
        if ruta.suffix == ".csv":
            frames.append(cargar_csv(ruta, low_memory=False))
        elif ruta.suffix in {".xlsx", ".xls"}:
            frames.append(cargar_excel(ruta))
        else:
            raise ValueError(f"Formato no soportado: {ruta.suffix}")
    if not frames:
        raise ValueError("La lista de rutas está vacía.")
    df = pd.concat(frames, ignore_index=True)
    print(f"[ingesta] Consolidación completada: {len(df):,} registros.")
    return df


def guardar_consolidado(df: pd.DataFrame) -> None:
    """
    Guarda el DataFrame consolidado como CSV y XLSX en datos/tarea_join/.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a guardar.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARCHIVO_CONSOLIDADO_CSV, index=False)
    df.to_excel(ARCHIVO_CONSOLIDADO_XLSX, index=False)
    print(f"[ingesta] Archivos guardados en {DATA_DIR}")


# ---------------------------------------------------------------------------
# Ejecución directa
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = cargar_consolidado()
    print(df.head())
