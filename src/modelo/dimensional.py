"""
Modelo dimensional en DuckDB — Investigadores reconocidos MinCiencias

Crea un esquema estrella a partir del consolidado de investigadores
con dimensiones de institución, área, categoría, municipio y convocatoria.
"""

import duckdb
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


def crear_dim_categoria(con):
    """Dimensión de clasificación del investigador (junior, asociado, senior, emérito)."""
    con.execute("DROP TABLE IF EXISTS dim_categoria")
    con.execute("""
        CREATE TABLE dim_categoria AS
        SELECT DISTINCT
            ID_CLAS_PR AS id_categoria,
            NME_CLASIFICACION_PR AS clasificacion,
            ORDEN_CLAS_PR AS orden
        FROM staging_investigadores
        WHERE ID_CLAS_PR IS NOT NULL
        ORDER BY ORDEN_CLAS_PR
    """)
    filas = con.execute("SELECT * FROM dim_categoria").fetchall()
    print(f"dim_categoria: {len(filas)} registros")
    for f in filas:
        print(f"  {f}")


def crear_dim_municipio(con):
    """Dimensión de municipio de residencia (jerarquía geográfica)."""
    con.execute("DROP TABLE IF EXISTS dim_municipio")
    con.execute("""
        CREATE TABLE dim_municipio AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY COD_DANE_RES_PR) AS id_municipio,
            COD_DANE_RES_PR AS cod_dane,
            NME_MUNICIPIO_RES_PR AS municipio,
            NME_DEPARTAMENTO_RES_PR AS departamento,
            NME_REGION_RES_PR AS region,
            NME_PAIS_RES_PR AS pais
        FROM (
            SELECT DISTINCT
                COD_DANE_RES_PR,
                NME_MUNICIPIO_RES_PR,
                NME_DEPARTAMENTO_RES_PR,
                NME_REGION_RES_PR,
                NME_PAIS_RES_PR
            FROM staging_investigadores
            WHERE COD_DANE_RES_PR IS NOT NULL
        )
        ORDER BY COD_DANE_RES_PR
    """)
    n = con.execute("SELECT count(*) FROM dim_municipio").fetchone()[0]
    print(f"dim_municipio: {n:,} registros")


def crear_fact_investigadores(con):
    """Tabla de hechos: un registro por investigador-convocatoria."""
    con.execute("DROP TABLE IF EXISTS fact_investigadores")
    con.execute("""
        CREATE TABLE fact_investigadores AS
        SELECT
            s.ID_PERSONA_PR,
            s.ID_CONVOCATORIA,
            di.id_institucion,
            da.id_area,
            s.ID_CLAS_PR AS id_categoria,
            dm.id_municipio,
            s.NME_GENERO_PR AS genero,
            s.EDAD_ANOS_PR AS edad,
            s.ID_VICTIMA_CONFLICTO AS victima_conflicto,
            s.TXT_GRUPO_ETNICO AS grupo_etnico,
            s.TXT_POBLACION_DISCA AS poblacion_discapacidad
        FROM staging_investigadores s
        LEFT JOIN dim_institucion di
            ON s.INST_FILIA = di.nombre_institucion
        LEFT JOIN dim_area da
            ON s.NME_GRAN_AREA_PR = da.gran_area
            AND s.NME_AREA_PR = da.area
            AND s.NME_ESP_AREA_PR = da.area_especifica
        LEFT JOIN dim_municipio dm
            ON s.COD_DANE_RES_PR = dm.cod_dane
    """)
    n = con.execute("SELECT count(*) FROM fact_investigadores").fetchone()[0]
    nulos = con.execute("""
        SELECT
            count(*) FILTER (WHERE id_institucion IS NULL) AS sin_inst,
            count(*) FILTER (WHERE id_area IS NULL) AS sin_area,
            count(*) FILTER (WHERE id_categoria IS NULL) AS sin_cat,
            count(*) FILTER (WHERE id_municipio IS NULL) AS sin_mun
        FROM fact_investigadores
    """).fetchone()
    print(f"fact_investigadores: {n:,} registros")
    print(f"  Nulos -> institucion: {nulos[0]}, area: {nulos[1]}, "
          f"categoria: {nulos[2]}, municipio: {nulos[3]}")


if __name__ == "__main__":
    con = conectar()
    cargar_csv(con)
    crear_dim_convocatoria(con)
    crear_dim_institucion(con)
    crear_dim_area(con)
    crear_dim_categoria(con)
    crear_dim_municipio(con)
    crear_fact_investigadores(con)

    # Limpiar staging
    con.execute("DROP TABLE IF EXISTS staging_investigadores")
    print("\nTablas finales:")
    tablas = con.execute("SHOW TABLES").fetchall()
    for t in tablas:
        n = con.execute(f"SELECT count(*) FROM {t[0]}").fetchone()[0]
        print(f"  {t[0]}: {n:,}")

    # Validaciones rapidas
    print("\nValidaciones:")
    r = con.execute("""
        SELECT dc.anio, dk.clasificacion, count(*) AS n
        FROM fact_investigadores f
        JOIN dim_convocatoria dc ON f.ID_CONVOCATORIA = dc.ID_CONVOCATORIA
        JOIN dim_categoria dk ON f.id_categoria = dk.id_categoria
        GROUP BY dc.anio, dk.clasificacion
        ORDER BY dc.anio, ANY_VALUE(dk.orden)
    """).fetchall()
    print("  Investigadores por anio y categoria:")
    for anio, clas, n in r:
        print(f"    {anio} | {clas}: {n:,}")

    r2 = con.execute("""
        SELECT dc.anio, genero, count(*) AS n
        FROM fact_investigadores f
        JOIN dim_convocatoria dc ON f.ID_CONVOCATORIA = dc.ID_CONVOCATORIA
        GROUP BY dc.anio, genero
        ORDER BY dc.anio, genero
    """).fetchall()
    print("  Investigadores por anio y genero:")
    for anio, gen, n in r2:
        print(f"    {anio} | {gen}: {n:,}")

    con.close()
    print(f"\nBase de datos: {DB_PATH}")
