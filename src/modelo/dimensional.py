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


def crear_dim_institucion(con):
    """Dimensión de institución de afiliación."""
    con.execute("DROP TABLE IF EXISTS dim_institucion")
    con.execute("""
        CREATE TABLE dim_institucion AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY INST_FILIA) AS id_institucion,
            INST_FILIA AS nombre_institucion
        FROM (
            SELECT DISTINCT INST_FILIA
            FROM staging_investigadores
            WHERE INST_FILIA IS NOT NULL
        )
        ORDER BY INST_FILIA
    """)
    n = con.execute("SELECT count(*) FROM dim_institucion").fetchone()[0]
    print(f"dim_institucion: {n:,} registros")


def crear_dim_area(con):
    """Dimensión de área del conocimiento (clasificación OCDE)."""
    con.execute("DROP TABLE IF EXISTS dim_area")
    con.execute("""
        CREATE TABLE dim_area AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY NME_GRAN_AREA_PR, NME_AREA_PR) AS id_area,
            NME_GRAN_AREA_PR AS gran_area,
            NME_AREA_PR AS area,
            NME_ESP_AREA_PR AS area_especifica
        FROM (
            SELECT DISTINCT
                NME_GRAN_AREA_PR,
                NME_AREA_PR,
                NME_ESP_AREA_PR
            FROM staging_investigadores
            WHERE NME_GRAN_AREA_PR IS NOT NULL
        )
        ORDER BY NME_GRAN_AREA_PR, NME_AREA_PR
    """)
    n = con.execute("SELECT count(*) FROM dim_area").fetchone()[0]
    print(f"dim_area: {n:,} registros")


if __name__ == "__main__":
    con = conectar()
    cargar_csv(con)
    crear_dim_convocatoria(con)
    crear_dim_institucion(con)
    crear_dim_area(con)
    con.close()
    print(f"\nBase de datos: {DB_PATH}")
