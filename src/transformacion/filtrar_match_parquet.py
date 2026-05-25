import os
from pathlib import Path

# Winutils para Windows: debe configurarse antes de importar PySpark.
if os.name == "nt":
    hadoop_home = os.environ.get("HADOOP_HOME", r"C:\hadoop")
    if os.path.isdir(hadoop_home):
        os.environ["HADOOP_HOME"] = hadoop_home
        hadoop_bin = os.path.join(hadoop_home, "bin")
        if os.path.isdir(hadoop_bin):
            os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


BASE_DIR = Path(os.environ.get("PROYECTO_BASE_DIR", Path(__file__).resolve().parent)).resolve()
INPUT_PARQUET = str(BASE_DIR / "consolidado_produccion_investigadores.parquet")
OUTPUT_PARQUET = str(BASE_DIR / "consolidado_produccion_investigadores_match.parquet")

MATCH_COLUMNS = [
    "INST_FILIA",
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
    "ID_VICTIMA_CONFLICTO",
    "TXT_GRUPO_ETNICO",
    "NME_GRAN_AREA_PR",
    "TXT_POBLACION_DISCA",
]


def invalid_value_condition(column_name):
    value = F.trim(F.coalesce(F.col(column_name).cast("string"), F.lit("")))
    return value.isNull() | (value == "") | (value == "0")


def invalid_count_expr(column_name):
    return F.sum(F.when(invalid_value_condition(column_name), 1).otherwise(0)).alias(column_name)


spark = (
    SparkSession.builder
    .appName("Filtrar_Match_Parquet")
    .config("spark.driver.memory", "4g")
    .config("spark.executor.memory", "4g")
    .config("spark.sql.shuffle.partitions", "50")
    .config("spark.ui.showConsoleProgress", "true")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

print("=" * 60)
print("PASO 1 - Leyendo parquet original...")
print("=" * 60)

df = spark.read.parquet(INPUT_PARQUET)
missing_columns = [column for column in MATCH_COLUMNS if column not in df.columns]
if missing_columns:
    raise ValueError(f"Faltan columnas requeridas para el match: {missing_columns}")

total_rows = df.count()
print(f"Registros en el parquet original: {total_rows:,}")

print("\n" + "=" * 60)
print("PASO 2 - Calculando filas invalidas en columnas de match...")
print("=" * 60)

invalid_before = df.agg(*[invalid_count_expr(column) for column in MATCH_COLUMNS]).collect()[0].asDict()

for column in MATCH_COLUMNS:
    print(f"{column:<28} invalidos antes: {int(invalid_before[column]):,}")

match_condition = None
for column in MATCH_COLUMNS:
    current_condition = ~invalid_value_condition(column)
    match_condition = current_condition if match_condition is None else (match_condition & current_condition)

print("\n" + "=" * 60)
print("PASO 3 - Filtrando solo filas con match valido...")
print("=" * 60)

df_match = df.filter(match_condition)
total_match = df_match.count()
removed_rows = total_rows - total_match

print(f"Registros con match valido: {total_match:,}")
print(f"Registros eliminados     : {removed_rows:,}")

print("\n" + "=" * 60)
print("PASO 4 - Validando el parquet filtrado...")
print("=" * 60)

invalid_after = df_match.agg(*[invalid_count_expr(column) for column in MATCH_COLUMNS]).collect()[0].asDict()
remaining_invalid = {column: int(value) for column, value in invalid_after.items() if int(value) > 0}

for column in MATCH_COLUMNS:
    print(f"{column:<28} invalidos despues: {int(invalid_after[column]):,}")

if remaining_invalid:
    raise ValueError(f"La validacion fallo. Siguen existiendo invalidos en: {remaining_invalid}")

print("\n" + "=" * 60)
print("PASO 5 - Escribiendo parquet filtrado...")
print("=" * 60)

(
    df_match
    .coalesce(1)
    .write
    .mode("overwrite")
    .parquet(OUTPUT_PARQUET)
)

print("\nProceso completado correctamente.")
print(f"Parquet original : {INPUT_PARQUET}")
print(f"Parquet filtrado : {OUTPUT_PARQUET}")
print(f"Filas finales    : {total_match:,}")
print(f"Columnas finales : {len(df_match.columns):,}")

spark.stop()