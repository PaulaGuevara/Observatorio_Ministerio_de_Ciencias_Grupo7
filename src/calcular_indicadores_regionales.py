"""
Issue #43 - Cálculo de indicadores regionales de producción científica.

Este script replica el cálculo de indicadores regionales a partir de la base
consolidada en formato Parquet.

Entrada esperada:
    datos/processed/consolidado_produccion_investigadores.parquet

Salidas:
    outputs/indicadores/*.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


RUTA_BASE = Path("datos/processed/consolidado_produccion_investigadores.parquet")
RUTA_SALIDA = Path("outputs/indicadores")


VALORES_REGION_INVALIDOS = {
    "",
    "NO DISPONIBLE",
    "SIN INFORMACIÓN",
    "SIN INFORMACION",
    "NO REPORTA",
    "NAN",
    "NONE",
}


def normalizar_texto(serie: pd.Series, valor_faltante: str) -> pd.Series:
    """
    Limpia una variable textual.

    Convierte valores nulos a una categoría explícita, elimina espacios
    extremos y evita cadenas vacías.
    """
    serie_limpia = serie.fillna(valor_faltante).astype(str).str.strip()
    serie_limpia = serie_limpia.replace("", valor_faltante)
    return serie_limpia


def validar_columnas(df: pd.DataFrame, columnas: list[str]) -> None:
    """
    Verifica que la base tenga las columnas mínimas necesarias.
    """
    faltantes = [col for col in columnas if col not in df.columns]

    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas para calcular los indicadores: "
            + ", ".join(faltantes)
        )


def preparar_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara la base para el cálculo de indicadores.

    El eje territorial principal es la región del grupo de investigación,
    porque los productos están asociados directamente a grupos.
    """
    df = df.copy()

    df["NME_REGION_GR"] = normalizar_texto(df["NME_REGION_GR"], "Sin información")
    df["NME_CLASIFICACION_GR"] = normalizar_texto(
        df["NME_CLASIFICACION_GR"],
        "Sin clasificación"
    )
    df["NME_TIPOLOGIA_PD"] = normalizar_texto(
        df["NME_TIPOLOGIA_PD"],
        "Sin tipología"
    )

    if "NME_GENERO_PR" in df.columns:
        df["NME_GENERO_PR"] = normalizar_texto(df["NME_GENERO_PR"], "Sin información")

    if "ID_CONVOCATORIA" in df.columns:
        df["ID_CONVOCATORIA"] = pd.to_numeric(
            df["ID_CONVOCATORIA"],
            errors="coerce"
        )

    return df


def filtrar_regiones_validas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excluye registros sin región territorial interpretable.
    """
    region_mayus = df["NME_REGION_GR"].str.upper().str.strip()
    return df.loc[~region_mayus.isin(VALORES_REGION_INVALIDOS)].copy()


def guardar(df: pd.DataFrame, nombre_archivo: str) -> None:
    """
    Guarda un indicador en formato CSV.
    """
    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = RUTA_SALIDA / nombre_archivo
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"Generado: {ruta}")


def indicador_01_produccion_total_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("NME_REGION_GR")
        .size()
        .reset_index(name="produccion_total")
        .sort_values("produccion_total", ascending=False)
    )


def indicador_02_participacion_region(produccion: pd.DataFrame) -> pd.DataFrame:
    total = produccion["produccion_total"].sum()

    salida = produccion.copy()
    salida["participacion_porcentual"] = (
        salida["produccion_total"] / total * 100
    ).round(2)

    return salida


def indicador_03_promedio_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    salida = (
        df.groupby("NME_REGION_GR")
        .agg(
            produccion_total=("COD_GRUPO_GR", "size"),
            grupos_unicos=("COD_GRUPO_GR", "nunique"),
        )
        .reset_index()
    )

    salida["produccion_promedio_por_grupo"] = (
        salida["produccion_total"] / salida["grupos_unicos"]
    ).round(2)

    return salida.sort_values("produccion_promedio_por_grupo", ascending=False)


def indicador_04_produccion_clasificacion_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["NME_REGION_GR", "NME_CLASIFICACION_GR"])
        .size()
        .reset_index(name="productos")
        .sort_values(["NME_REGION_GR", "productos"], ascending=[True, False])
    )


def indicador_05_diversidad_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("NME_REGION_GR")
        .agg(
            tipologias_distintas=("NME_TIPOLOGIA_PD", "nunique"),
            productos_considerados=("NME_TIPOLOGIA_PD", "size"),
        )
        .reset_index()
        .sort_values("tipologias_distintas", ascending=False)
    )


def indicador_06_especializacion_productiva(df: pd.DataFrame) -> pd.DataFrame:
    salida = (
        df.groupby("NME_REGION_GR")
        .agg(
            productos=("COD_GRUPO_GR", "size"),
            grupos_unicos=("COD_GRUPO_GR", "nunique"),
        )
        .reset_index()
    )

    total_productos = salida["productos"].sum()
    total_grupos = salida["grupos_unicos"].sum()

    salida["participacion_productos"] = (
        salida["productos"] / total_productos * 100
    ).round(2)

    salida["participacion_grupos"] = (
        salida["grupos_unicos"] / total_grupos * 100
    ).round(2)

    salida["indice_especializacion_productiva"] = (
        salida["participacion_productos"] / salida["participacion_grupos"]
    ).round(2)

    return salida.sort_values("indice_especializacion_productiva", ascending=False)


def indicador_07_diversidad_relativa(df: pd.DataFrame) -> pd.DataFrame:
    total_tipologias = df["NME_TIPOLOGIA_PD"].nunique()

    salida = indicador_05_diversidad_region(df)
    salida["total_tipologias_nacionales"] = total_tipologias
    salida["diversidad_relativa_porcentual"] = (
        salida["tipologias_distintas"] / total_tipologias * 100
    ).round(2)

    return salida.sort_values("diversidad_relativa_porcentual", ascending=False)


def indicador_08_permanencia_grupos(df: pd.DataFrame) -> pd.DataFrame:
    base = df.dropna(subset=["ID_CONVOCATORIA"]).copy()

    grupos_conv = (
        base.groupby(["NME_REGION_GR", "COD_GRUPO_GR"])
        .agg(convocatorias_presentes=("ID_CONVOCATORIA", "nunique"))
        .reset_index()
    )

    salida = (
        grupos_conv.groupby("NME_REGION_GR")
        .agg(
            grupos_unicos=("COD_GRUPO_GR", "nunique"),
            grupos_permanentes=("convocatorias_presentes", lambda x: (x >= 3).sum()),
        )
        .reset_index()
    )

    salida["tasa_permanencia_grupos"] = (
        salida["grupos_permanentes"] / salida["grupos_unicos"] * 100
    ).round(2)

    return salida.sort_values("tasa_permanencia_grupos", ascending=False)


def indicador_09_crecimiento_grupos(df: pd.DataFrame) -> pd.DataFrame:
    base = df.dropna(subset=["ID_CONVOCATORIA"]).copy()

    grupos = (
        base.groupby(["NME_REGION_GR", "ID_CONVOCATORIA"])["COD_GRUPO_GR"]
        .nunique()
        .reset_index(name="grupos")
    )

    tabla = grupos.pivot(
        index="NME_REGION_GR",
        columns="ID_CONVOCATORIA",
        values="grupos"
    ).fillna(0)

    for convocatoria in [2017, 2019, 2021]:
        if convocatoria not in tabla.columns:
            tabla[convocatoria] = 0

    tabla = tabla.reset_index()
    tabla = tabla.rename(
        columns={
            2017: "grupos_2017",
            2019: "grupos_2019",
            2021: "grupos_2021",
        }
    )

    tabla["crecimiento_neto_grupos"] = (
        tabla["grupos_2021"] - tabla["grupos_2017"]
    )

    tabla["crecimiento_porcentual_grupos"] = np.where(
        tabla["grupos_2017"] > 0,
        tabla["crecimiento_neto_grupos"] / tabla["grupos_2017"] * 100,
        np.nan,
    )

    tabla["crecimiento_porcentual_grupos"] = (
        tabla["crecimiento_porcentual_grupos"].round(2)
    )

    return tabla.sort_values("crecimiento_porcentual_grupos", ascending=False)


def indicador_10_fortaleza_a1_a_2021(df: pd.DataFrame) -> pd.DataFrame:
    base = df.loc[df["ID_CONVOCATORIA"] == 2021].copy()

    grupos = base[
        ["NME_REGION_GR", "COD_GRUPO_GR", "NME_CLASIFICACION_GR"]
    ].drop_duplicates()

    salida = (
        grupos.groupby("NME_REGION_GR")
        .agg(
            grupos_clasificados_2021=("COD_GRUPO_GR", "nunique"),
            grupos_a1_a_2021=(
                "NME_CLASIFICACION_GR",
                lambda x: x.isin(["A1", "A"]).sum()
            ),
        )
        .reset_index()
    )

    salida["fortaleza_a1_a_2021"] = (
        salida["grupos_a1_a_2021"] / salida["grupos_clasificados_2021"] * 100
    ).round(2)

    return salida.sort_values("fortaleza_a1_a_2021", ascending=False)


def indicador_11_renovacion_grupos(df: pd.DataFrame) -> pd.DataFrame:
    base = df.dropna(subset=["ID_CONVOCATORIA"]).copy()

    grupos_2017 = (
        base.loc[base["ID_CONVOCATORIA"] == 2017, ["NME_REGION_GR", "COD_GRUPO_GR"]]
        .drop_duplicates()
    )

    grupos_2021 = (
        base.loc[base["ID_CONVOCATORIA"] == 2021, ["NME_REGION_GR", "COD_GRUPO_GR"]]
        .drop_duplicates()
    )

    grupos_2017["presente_2017"] = True

    comparacion = grupos_2021.merge(
        grupos_2017,
        on=["NME_REGION_GR", "COD_GRUPO_GR"],
        how="left"
    )

    comparacion["grupo_nuevo"] = comparacion["presente_2017"].isna()

    salida = (
        comparacion.groupby("NME_REGION_GR")
        .agg(
            grupos_2021=("COD_GRUPO_GR", "nunique"),
            grupos_nuevos_2021_vs_2017=("grupo_nuevo", "sum"),
        )
        .reset_index()
    )

    salida["tasa_renovacion_grupos"] = (
        salida["grupos_nuevos_2021_vs_2017"] / salida["grupos_2021"] * 100
    ).round(2)

    return salida.sort_values("tasa_renovacion_grupos", ascending=False)


def indicador_12_genero_region(df: pd.DataFrame) -> pd.DataFrame:
    if "NME_GENERO_PR" not in df.columns:
        return pd.DataFrame()

    if "ID_PERSONA_PR" in df.columns:
        investigador_col = "ID_PERSONA_PR"
    elif "ID_PERSONA_PD" in df.columns:
        investigador_col = "ID_PERSONA_PD"
    else:
        investigador_col = "COD_GRUPO_GR"

    salida = (
        df.groupby(["NME_REGION_GR", "NME_GENERO_PR"])
        .agg(
            productos=("NME_GENERO_PR", "size"),
            investigadores_unicos=(investigador_col, "nunique"),
        )
        .reset_index()
    )

    total_region = (
        salida.groupby("NME_REGION_GR")["productos"]
        .sum()
        .reset_index(name="total_productos_region")
    )

    salida = salida.merge(total_region, on="NME_REGION_GR", how="left")

    salida["participacion_porcentual_genero_region"] = (
        salida["productos"] / salida["total_productos_region"] * 100
    ).round(2)

    salida["produccion_promedio_por_investigador"] = (
        salida["productos"] / salida["investigadores_unicos"]
    ).round(2)

    return salida.sort_values(["NME_REGION_GR", "productos"], ascending=[True, False])


def indicador_13_evolucion_grupos_detalle(df: pd.DataFrame) -> pd.DataFrame:
    base = df.dropna(subset=["ID_CONVOCATORIA"]).copy()

    return (
        base.groupby(["NME_REGION_GR", "ID_CONVOCATORIA"])
        .agg(
            grupos_unicos=("COD_GRUPO_GR", "nunique"),
            productos=("COD_GRUPO_GR", "size"),
        )
        .reset_index()
        .sort_values(["NME_REGION_GR", "ID_CONVOCATORIA"])
    )


def indicador_14_evolucion_grupos_region(df: pd.DataFrame) -> pd.DataFrame:
    detalle = indicador_13_evolucion_grupos_detalle(df)

    tabla = detalle.pivot(
        index="NME_REGION_GR",
        columns="ID_CONVOCATORIA",
        values="grupos_unicos"
    ).fillna(0)

    for convocatoria in [2017, 2019, 2021]:
        if convocatoria not in tabla.columns:
            tabla[convocatoria] = 0

    tabla = tabla.reset_index()
    tabla = tabla.rename(
        columns={
            2017: "grupos_2017",
            2019: "grupos_2019",
            2021: "grupos_2021",
        }
    )

    tabla["variacion_2017_2021"] = tabla["grupos_2021"] - tabla["grupos_2017"]

    return tabla.sort_values("variacion_2017_2021", ascending=False)


def indicador_15_participacion_clasificacion_region(df: pd.DataFrame) -> pd.DataFrame:
    salida = indicador_04_produccion_clasificacion_region(df)

    total_region = (
        salida.groupby("NME_REGION_GR")["productos"]
        .sum()
        .reset_index(name="total_productos_region")
    )

    salida = salida.merge(total_region, on="NME_REGION_GR", how="left")

    salida["participacion_clasificacion_region"] = (
        salida["productos"] / salida["total_productos_region"] * 100
    ).round(2)

    return salida.sort_values(
        ["NME_REGION_GR", "participacion_clasificacion_region"],
        ascending=[True, False]
    )


def indicador_16_participacion_clasificacion_region_convocatoria(
    df: pd.DataFrame,
) -> pd.DataFrame:
    base = df.dropna(subset=["ID_CONVOCATORIA"]).copy()

    salida = (
        base.groupby(["ID_CONVOCATORIA", "NME_REGION_GR", "NME_CLASIFICACION_GR"])
        .size()
        .reset_index(name="productos")
    )

    total_region_conv = (
        salida.groupby(["ID_CONVOCATORIA", "NME_REGION_GR"])["productos"]
        .sum()
        .reset_index(name="total_productos_region_convocatoria")
    )

    salida = salida.merge(
        total_region_conv,
        on=["ID_CONVOCATORIA", "NME_REGION_GR"],
        how="left"
    )

    salida["participacion_clasificacion_region_convocatoria"] = (
        salida["productos"] / salida["total_productos_region_convocatoria"] * 100
    ).round(2)

    return salida.sort_values(
        ["ID_CONVOCATORIA", "NME_REGION_GR", "participacion_clasificacion_region_convocatoria"],
        ascending=[True, True, False]
    )


def main() -> None:
    if not RUTA_BASE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de entrada: {RUTA_BASE}"
        )

    df = pd.read_parquet(RUTA_BASE)

    columnas_requeridas = [
        "NME_REGION_GR",
        "COD_GRUPO_GR",
        "NME_CLASIFICACION_GR",
        "NME_TIPOLOGIA_PD",
        "ID_CONVOCATORIA",
    ]

    validar_columnas(df, columnas_requeridas)

    df = preparar_base(df)
    df = filtrar_regiones_validas(df)

    ind_01 = indicador_01_produccion_total_region(df)
    ind_02 = indicador_02_participacion_region(ind_01)
    ind_03 = indicador_03_promedio_por_grupo(df)
    ind_04 = indicador_04_produccion_clasificacion_region(df)
    ind_05 = indicador_05_diversidad_region(df)
    ind_06 = indicador_06_especializacion_productiva(df)
    ind_07 = indicador_07_diversidad_relativa(df)
    ind_08 = indicador_08_permanencia_grupos(df)
    ind_09 = indicador_09_crecimiento_grupos(df)
    ind_10 = indicador_10_fortaleza_a1_a_2021(df)
    ind_11 = indicador_11_renovacion_grupos(df)
    ind_12 = indicador_12_genero_region(df)
    ind_13 = indicador_13_evolucion_grupos_detalle(df)
    ind_14 = indicador_14_evolucion_grupos_region(df)
    ind_15 = indicador_15_participacion_clasificacion_region(df)
    ind_16 = indicador_16_participacion_clasificacion_region_convocatoria(df)

    guardar(ind_01, "01_produccion_total_region.csv")
    guardar(ind_02, "02_participacion_region.csv")
    guardar(ind_03, "03_promedio_por_grupo_region.csv")
    guardar(ind_04, "04_produccion_clasificacion_region.csv")
    guardar(ind_05, "05_diversidad_region.csv")
    guardar(ind_06, "06_indice_especializacion_productiva.csv")
    guardar(ind_07, "07_diversidad_relativa_region.csv")
    guardar(ind_08, "08_permanencia_grupos_region.csv")
    guardar(ind_09, "09_crecimiento_grupos_region.csv")
    guardar(ind_10, "10_fortaleza_a1_a_2021_region.csv")
    guardar(ind_11, "11_renovacion_grupos_region.csv")

    if not ind_12.empty:
        guardar(ind_12, "12_genero_region.csv")

    guardar(ind_13, "13_evolucion_grupos_detalle.csv")
    guardar(ind_14, "14_evolucion_grupos_region.csv")
    guardar(ind_15, "15_participacion_clasificacion_region.csv")
    guardar(ind_16, "16_participacion_clasificacion_region_convocatoria.csv")

    print("\nResumen de validación")
    print(f"Registros procesados: {len(df):,}")
    print(f"Regiones válidas: {df['NME_REGION_GR'].nunique():,}")
    print(f"Grupos únicos: {df['COD_GRUPO_GR'].nunique():,}")
    print(f"Suma participación regional: {ind_02['participacion_porcentual'].sum():.2f}%")
    print("Cálculo de indicadores finalizado correctamente.")


if __name__ == "__main__":
    main()
