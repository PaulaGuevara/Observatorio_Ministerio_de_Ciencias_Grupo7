"""
Script PySpark para consolidar las 7 bases de investigación en un solo archivo Parquet.

Estrategia:
  1. Unir los 4 archivos de investigadores (investigadores_consolidado + 3 Reconocidos)
     → todos comparten las mismas columnas, clave: (ID_PERSONA_PR, ID_CONVOCATORIA)
  2. Unir los 3 archivos de Producción → clave: (ID_PERSONA_PD, ID_CONVOCATORIA)
  3. LEFT JOIN producción ← investigadores sobre
         ID_PERSONA_PD = ID_PERSONA_PR  AND  producción.ID_CONVOCATORIA = inv.ID_CONVOCATORIA
     para enriquecer cada producto con las características del investigador correspondiente.

Salida: consolidado_produccion_investigadores.parquet
"""

import os
from pathlib import Path

# ─── Winutils para Windows (debe ir ANTES de importar PySpark) ────────────────
if os.name == "nt":
    hadoop_home = os.environ.get("HADOOP_HOME", r"C:\hadoop")
    if os.path.isdir(hadoop_home):
        os.environ["HADOOP_HOME"] = hadoop_home
        hadoop_bin = os.path.join(hadoop_home, "bin")
        if os.path.isdir(hadoop_bin):
            os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ─── Configuración ────────────────────────────────────────────────────────────
BASE_DIR = Path(os.environ.get("PROYECTO_BASE_DIR", Path(__file__).resolve().parent)).resolve()
OUTPUT = str(BASE_DIR / "consolidado_produccion_investigadores.parquet")

# Archivos de investigadores (mismas columnas, se unen con UNION ALL)
INVESTIGADORES = [
    str(BASE_DIR / "investigadores_consolidado.csv"),
    str(BASE_DIR / "Investigadores_Reconocidos_por_convocatoria_2017.csv"),
    str(BASE_DIR / "Investigadores_Reconocidos_por_convocatoria_2019.csv"),
    str(BASE_DIR / "Investigadores_Reconocidos_por_convocatoria_2021.csv"),
]

# Archivos de producción (mismas columnas, se unen con UNION ALL)
PRODUCCION = [
    str(BASE_DIR / "Producción_Grupos_Investigación_20260421 2017.csv"),
    str(BASE_DIR / "Producción_Grupos_Investigación_20260421 2019.csv"),
    str(BASE_DIR / "Producción_Grupos_Investigación_20260421 2021.csv"),
]

# Columnas a conservar del bloque de investigadores (después del JOIN)
COLS_INV = [
    "ID_PERSONA_PR",
    "NME_GENERO_PR",
    "NME_PAIS_NAC_PR",
    "NME_REGION_NAC_PR",
    "NME_DEPARTAMENTO_NAC_PR",
    "NME_MUNICIPIO_NAC_PR",
    "NME_NIV_FORM_PR",
    "NME_CLASIFICACION_PR",
    "EDAD_ANOS_PR",
    "NME_DEPARTAMENTO_RES_PR",
    "NME_REGION_RES_PR",
    "NME_PAIS_RES_PR",
    "INST_FILIA",
    "ID_VICTIMA_CONFLICTO",
    "TXT_GRUPO_ETNICO",
    "NME_GRAN_AREA_PR",
    "TXT_POBLACION_DISCA",
]

# Archivos de grupos de investigación (mismas columnas, se unen con UNION ALL)
GRUPOS = [
    str(BASE_DIR / "Grupos_de_Investigación_Reconocidos_20260430 2017.csv"),
    str(BASE_DIR / "Grupos_de_Investigación_Reconocidos_20260430 2019.csv"),
    str(BASE_DIR / "Grupos_de_Investigación_Reconocidos_20260430 2021.csv"),
]

# Columnas a conservar del bloque de grupos (además de la llave de join)
COLS_GR = [
    "INST_AVAL",
    "NME_CLASIFICACION_GR",
    "NME_PAIS_GR",
    "NME_REGION_GR",
    "NME_DEPARTAMENTO_GR",
    "NME_MUNICIPIO_GR",
]

# Columnas a conservar del bloque de producción
COLS_PROD = [
    "ID_CONVOCATORIA",
    "NME_CONVOCATORIA",
    "ANO_CONVO",
    "ID_PERSONA_PD",
    "NME_CLASE_PD",
    "NME_TIPO_MEDICION_PD",
    "NME_TIPOLOGIA_PD",
    "ID_TIPO_PD_MED",
    "NME_CATEGORIA_PD",
    "COD_GRUPO_GR",
]

# ─── Inicializar Spark ─────────────────────────────────────────────────────────
spark = (
    SparkSession.builder
    .appName("Consolidar_Investigacion")
    # Limita el uso de memoria del driver y executor para equipos con RAM ajustada
    .config("spark.driver.memory", "4g")
    .config("spark.executor.memory", "4g")
    # Particiones para shuffle reducidas (datos ~900 MB total)
    .config("spark.sql.shuffle.partitions", "50")
    # Evita logs excesivos
    .config("spark.ui.showConsoleProgress", "true")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

print("=" * 60)
print("PASO 1 – Cargando y uniendo archivos de investigadores...")
print("=" * 60)

def read_csv(path):
    """Lee un CSV con encabezado, inferencia de tipos y manejo de comillas."""
    return (
        spark.read
        .option("header", "true")
        .option("inferSchema", "false")   # todo como string; evita errores de tipo
        .option("quote", '"')
        .option("escape", '"')
        .option("multiLine", "true")
        .option("encoding", "UTF-8")
        .csv(path)
    )

# Unir los 4 archivos de investigadores
df_inv_list = [read_csv(p) for p in INVESTIGADORES]
df_inv = df_inv_list[0]
for df in df_inv_list[1:]:
    df_inv = df_inv.unionByName(df, allowMissingColumns=True)

# Deduplicar por (ID_PERSONA_PR, ID_CONVOCATORIA) para evitar producto cartesiano en el JOIN
# Se conserva la primera aparición (el orden de los archivos actúa como prioridad)
df_inv = (
    df_inv
    .select(["ID_CONVOCATORIA", "ID_PERSONA_PR"] + [c for c in COLS_INV if c != "ID_PERSONA_PR"])
    .dropDuplicates(["ID_PERSONA_PR", "ID_CONVOCATORIA"])
)

print(f"   Registros únicos de investigadores: {df_inv.count():,}")

print("\n" + "=" * 60)
print("PASO 2 – Cargando y uniendo archivos de producción...")
print("=" * 60)

df_prod_list = [read_csv(p) for p in PRODUCCION]
df_prod = df_prod_list[0]
for df in df_prod_list[1:]:
    df_prod = df_prod.unionByName(df, allowMissingColumns=True)

df_prod = df_prod.select(COLS_PROD)

print(f"   Registros de producción: {df_prod.count():,}")

print("\n" + "=" * 60)
print("PASO 3 – JOIN producción ← investigadores...")
print("=" * 60)
# LEFT JOIN: se conservan todos los registros de producción aunque no haya
# coincidencia en el archivo de investigadores.
# Clave compuesta: persona + convocatoria (misma convocatoria = misma medición)
df_consolidado = (
    df_prod.alias("prod")
    .join(
        df_inv.alias("inv"),
        on=[
            F.col("prod.ID_PERSONA_PD") == F.col("inv.ID_PERSONA_PR"),
            F.col("prod.ID_CONVOCATORIA") == F.col("inv.ID_CONVOCATORIA"),
        ],
        how="left",
    )
    .select(
        # — Producción —
        F.col("prod.ID_CONVOCATORIA"),
        F.col("prod.NME_CONVOCATORIA"),
        F.col("prod.ANO_CONVO"),
        F.col("prod.ID_PERSONA_PD"),
        F.col("prod.NME_CLASE_PD"),
        F.col("prod.NME_TIPO_MEDICION_PD"),
        F.col("prod.NME_TIPOLOGIA_PD"),
        F.col("prod.ID_TIPO_PD_MED"),
        F.col("prod.NME_CATEGORIA_PD"),
        F.col("prod.COD_GRUPO_GR"),
        # — Investigador (del JOIN) —
        F.col("inv.ID_PERSONA_PR"),
        F.col("inv.NME_GENERO_PR"),
        F.col("inv.NME_PAIS_NAC_PR"),
        F.col("inv.NME_REGION_NAC_PR"),
        F.col("inv.NME_DEPARTAMENTO_NAC_PR"),
        F.col("inv.NME_MUNICIPIO_NAC_PR"),
        F.col("inv.NME_NIV_FORM_PR"),
        F.col("inv.NME_CLASIFICACION_PR"),
        F.col("inv.EDAD_ANOS_PR"),
        F.col("inv.NME_DEPARTAMENTO_RES_PR"),
        F.col("inv.NME_REGION_RES_PR"),
        F.col("inv.NME_PAIS_RES_PR"),
        F.col("inv.INST_FILIA"),
        F.col("inv.ID_VICTIMA_CONFLICTO"),
        F.col("inv.TXT_GRUPO_ETNICO"),
        F.col("inv.NME_GRAN_AREA_PR"),
        F.col("inv.TXT_POBLACION_DISCA"),
    )
)

print("\n" + "=" * 60)
print("PASO 3.5 – Cargando y uniendo archivos de grupos de investigación...")
print("=" * 60)

df_gr_list = [read_csv(p) for p in GRUPOS]
df_gr = df_gr_list[0]
for df in df_gr_list[1:]:
    df_gr = df_gr.unionByName(df, allowMissingColumns=True)

# Seleccionar llave de join + columnas de interés y deduplicar por (COD_GRUPO_GR, ID_CONVOCATORIA)
# para preservar la clasificación correcta según convocatoria
df_gr = (
    df_gr
    .select(["COD_GRUPO_GR", "ID_CONVOCATORIA"] + COLS_GR)
    .dropDuplicates(["COD_GRUPO_GR", "ID_CONVOCATORIA"])
)

print(f"   Registros únicos de grupos: {df_gr.count():,}")

print("\n" + "=" * 60)
print("PASO 3.6 – JOIN consolidado ← grupos...")
print("=" * 60)

df_consolidado = (
    df_consolidado.alias("cons")
    .join(
        df_gr.alias("gr"),
        on=[
            F.col("cons.COD_GRUPO_GR") == F.col("gr.COD_GRUPO_GR"),
            F.col("cons.ID_CONVOCATORIA") == F.col("gr.ID_CONVOCATORIA"),
        ],
        how="left",
    )
    .select(
        F.col("cons.*"),
        F.col("gr.INST_AVAL"),
        F.col("gr.NME_CLASIFICACION_GR"),
        F.col("gr.NME_PAIS_GR"),
        F.col("gr.NME_REGION_GR"),
        F.col("gr.NME_DEPARTAMENTO_GR"),
        F.col("gr.NME_MUNICIPIO_GR"),
    )
)

print("\n" + "=" * 60)
print("PASO 4 – Escribiendo archivo Parquet...")
print("=" * 60)

(
    df_consolidado
    .coalesce(1)           # un solo archivo Parquet de salida
    .write
    .mode("overwrite")
    .parquet(OUTPUT)
)

total = df_consolidado.count()
print(f"\n✓ Consolidación completada.")
print(f"  Registros totales en el Parquet : {total:,}")
print(f"  Ubicación del archivo           : {OUTPUT}")

# Verificación rápida del esquema de salida
print("\n── Esquema del archivo consolidado ──────────────────────")
df_consolidado.printSchema()

spark.stop()
