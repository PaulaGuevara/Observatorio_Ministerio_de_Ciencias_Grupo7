"""
Modelo dimensional en DuckDB — Investigadores reconocidos MinCiencias

Crea un esquema estrella a partir del consolidado de investigadores
con dimensiones de institución, área, categoría, municipio y convocatoria.
"""

import duckdb
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
DB_PATH = ROOT / "datos" / "processed" / "observatorio.duckdb"


def conectar():
    """Crea o abre la base de datos DuckDB."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def cargar_csv(con):
    """Carga el CSV consolidado como tabla staging."""
    con.execute("DROP TABLE IF EXISTS staging_investigadores")
    con.execute(f"""
        CREATE TABLE staging_investigadores AS
        SELECT * FROM read_csv_auto('{CSV_PATH.as_posix()}', header=true)
    """)
    n = con.execute("SELECT count(*) FROM staging_investigadores").fetchone()[0]
    print(f"Staging: {n:,} registros cargados")
    return n


def crear_dim_convocatoria(con):
    """Dimensión de convocatoria (2017, 2019, 2021)."""
    con.execute("DROP TABLE IF EXISTS dim_convocatoria")
    con.execute("""
        CREATE TABLE dim_convocatoria AS
        SELECT DISTINCT
            ID_CONVOCATORIA,
            NME_CONVOCATORIA,
            CAST(strftime(
                TRY_CAST(ANO_CONVO AS DATE), '%Y'
            ) AS INTEGER) AS anio
        FROM staging_investigadores
        WHERE ID_CONVOCATORIA IS NOT NULL
        ORDER BY anio
    """)
    filas = con.execute("SELECT * FROM dim_convocatoria").fetchall()
    print(f"dim_convocatoria: {len(filas)} registros")
    for f in filas:
        print(f"  {f}")


if __name__ == "__main__":
    con = conectar()
    cargar_csv(con)
    crear_dim_convocatoria(con)
    con.close()
    print(f"\nBase de datos: {DB_PATH}")
