from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.visualizacion.distribuciones_mariap import (
    figura_distribucion_categoria,
    figura_distribucion_genero,
    preparar_distribucion_categoria,
    preparar_distribucion_genero,
)
from src.visualizacion.instituciones import (
    expandir_instituciones,
    filtrar_instituciones,
    figura_ranking_instituciones,
    obtener_columna_area,
    ranking_instituciones,
)
from src.visualizacion.mapas_mariap import (
    figura_mapa_departamentos,
    tabla_top_departamentos,
)

CSV_PATH = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"

COLUMNAS_BASE = [
    "ANO_CONVO",
    "ID_PERSONA_PR",
    "NME_CLASIFICACION_PR",
    "NME_GENERO_PR",
]


def normalizar_anio(serie: pd.Series) -> pd.Series:
    anio_num = pd.to_numeric(serie, errors="coerce")
    anio_fecha = pd.to_datetime(serie, dayfirst=True, errors="coerce").dt.year
    anio_final = anio_num.where(anio_num.between(1900, 2100), anio_fecha)
    return anio_final.astype("Int64")


def crear_alias_columnas(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    base = df.copy()
    avisos = []

    if "NME_DEPARTAMENTO_RES_PR" not in base.columns:
        if "NME_DEPARTAMENTO_NAC_PR" in base.columns:
            base["NME_DEPARTAMENTO_RES_PR"] = base["NME_DEPARTAMENTO_NAC_PR"]
            avisos.append(
                "No se encontró 'NME_DEPARTAMENTO_RES_PR'. "
                "Se usó 'NME_DEPARTAMENTO_NAC_PR' como reemplazo."
            )

    if "INST_FILIA" not in base.columns:
        alternativas_inst = [
            "INST_AVAL",
            "NME_INST_PR",
            "NME_INSTITUCION_PR",
            "INSTITUCION",
        ]
        for col in alternativas_inst:
            if col in base.columns:
                base["INST_FILIA"] = base[col]
                avisos.append(
                    f"No se encontró 'INST_FILIA'. Se usó '{col}' como reemplazo."
                )
                break

    return base, avisos


def validar_columnas_base(df: pd.DataFrame) -> None:
    faltantes = [col for col in COLUMNAS_BASE if col not in df.columns]
    if faltantes:
        raise ValueError(
            "Faltan columnas base requeridas en el consolidado: "
            + ", ".join(faltantes)
        )


@st.cache_data(show_spinner="Cargando consolidado de investigadores...")
def cargar_datos() -> tuple[pd.DataFrame, list[str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, low_memory=False)
    df, avisos = crear_alias_columnas(df)
    validar_columnas_base(df)

    df = df.copy()
    df["ANO_CONVO"] = normalizar_anio(df["ANO_CONVO"])
    df = df[df["ANO_CONVO"].isin([2017, 2019, 2021])].copy()

    df["NME_CLASIFICACION_PR"] = (
        df["NME_CLASIFICACION_PR"].fillna("No registra").astype(str).str.strip()
    )
    df["NME_GENERO_PR"] = (
        df["NME_GENERO_PR"].fillna("No registra").astype(str).str.strip()
    )

    if "NME_DEPARTAMENTO_RES_PR" in df.columns:
        df["NME_DEPARTAMENTO_RES_PR"] = (
            df["NME_DEPARTAMENTO_RES_PR"]
            .fillna("No registra")
            .astype(str)
            .str.strip()
        )

    if "INST_FILIA" in df.columns:
        df["INST_FILIA"] = df["INST_FILIA"].fillna("").astype(str).str.strip()

    columna_area = obtener_columna_area(df)
    if columna_area is not None:
        df[columna_area] = (
            df[columna_area].fillna("No registra").astype(str).str.strip()
        )

    return df, avisos


def formatear_tabla_departamentos(df_tabla: pd.DataFrame) -> pd.DataFrame:
    base = df_tabla.copy()
    if base.empty:
        return base

    base["Investigadores"] = base["Investigadores"].map(lambda x: f"{x:,}")
    base["% del total"] = base["% del total"].map(lambda x: f"{x:.2f}%")
    return base


def formatear_tabla_ranking(df_tabla: pd.DataFrame) -> pd.DataFrame:
    base = df_tabla.copy()
    if base.empty:
        return base

    base = base.rename(
        columns={
            "ranking": "Ranking",
            "institucion": "Institución",
            "n_investigadores": "Investigadores únicos",
        }
    )
    base["Investigadores únicos"] = base["Investigadores únicos"].map(
        lambda x: f"{x:,}"
    )
    return base


def resumen_issue_19(df_anio: pd.DataFrame) -> str:
    categoria_df = preparar_distribucion_categoria(df_anio)
    genero_df = preparar_distribucion_genero(df_anio)

    categoria_top = (
        categoria_df.sort_values("n_investigadores", ascending=False)
        .iloc[0]["NME_CLASIFICACION_PR"]
        if not categoria_df.empty
        else "No disponible"
    )
    genero_top = (
        genero_df.sort_values("n_investigadores", ascending=False)
        .iloc[0]["NME_GENERO_PR"]
        if not genero_df.empty
        else "No disponible"
    )

    total = df_anio["ID_PERSONA_PR"].nunique()
    return (
        f"En la convocatoria seleccionada se registran **{total:,} investigadores únicos**. "
        f"La categoría con mayor participación es **{categoria_top}** y el género con mayor presencia es **{genero_top}**."
    )


def resumen_issue_20(ranking_df: pd.DataFrame, anio_sel: int) -> str:
    if ranking_df.empty:
        return "No hay información suficiente para construir una interpretación del ranking."

    top_inst = ranking_df.iloc[0]["institucion"]
    top_val = ranking_df.iloc[0]["n_investigadores"]

    return (
        f"Para la convocatoria **{anio_sel}**, la institución con mayor número de investigadores es "
        f"**{top_inst}**, con **{top_val:,} investigadores únicos**."
    )


st.set_page_config(
    page_title="Observatorio MinCiencias",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 96%;
    }

    h1 {
        font-size: 2.4rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        font-size: 1.6rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
    }

    .stCaption, p, label, div {
        font-size: 0.98rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Observatorio MinCiencias — Sprint 3")

try:
    df_global, avisos_carga = cargar_datos()
except Exception as exc:
    st.error(f"No fue posible cargar el dashboard: {exc}")
    st.stop()

for aviso in avisos_carga:
    st.warning(aviso)

anios_disponibles = sorted(
    [
        anio
        for anio in df_global["ANO_CONVO"].dropna().unique().tolist()
        if anio in [2017, 2019, 2021]
    ]
)

if not anios_disponibles:
    st.error("No hay registros válidos para 2017, 2019 o 2021.")
    st.stop()

with st.sidebar:
    st.header("Navegación")
    seccion = st.radio(
        "Selecciona una vista",
        ["Issue 19 · Mapa territorial", "Issue 20 · Ranking de instituciones"],
    )

    st.divider()
    st.subheader("Filtro temporal")
    anio_sel = st.select_slider(
        "Convocatoria",
        options=anios_disponibles,
        value=anios_disponibles[-1],
    )

    categoria_sel = "Todas"
    area_sel = "Todas"
    top_n = 15

    if seccion == "Issue 20 · Ranking de instituciones":
        st.divider()
        st.subheader("Filtros del ranking")

        categorias = ["Todas"] + sorted(
            df_global["NME_CLASIFICACION_PR"].dropna().unique().tolist()
        )
        categoria_sel = st.selectbox("Categoría", categorias, index=0)

        columna_area_sidebar = obtener_columna_area(df_global)
        if columna_area_sidebar is not None:
            areas = ["Todas"] + sorted(
                df_global[columna_area_sidebar].dropna().unique().tolist()
            )
            area_sel = st.selectbox("Área", areas, index=0)
        else:
            st.info("No se encontró una columna de área disponible.")

        top_n = st.slider("Top N", min_value=5, max_value=30, value=15, step=1)

df_anio = df_global[df_global["ANO_CONVO"] == anio_sel].copy()

if seccion == "Issue 19 · Mapa territorial":
    st.subheader("Issue 19 — Mapa por departamento y distribuciones")
    st.caption(
        "Vista territorial de investigadores por departamento, complementada con la distribución por categoría y género."
    )

    total_inv = df_anio["ID_PERSONA_PR"].nunique()
    total_deptos = (
        df_anio["NME_DEPARTAMENTO_RES_PR"].nunique()
        if "NME_DEPARTAMENTO_RES_PR" in df_anio.columns
        else 0
    )

    categoria_df = preparar_distribucion_categoria(df_anio)
    categoria_top = (
        categoria_df.sort_values("n_investigadores", ascending=False)
        .iloc[0]["NME_CLASIFICACION_PR"]
        if not categoria_df.empty
        else "No disponible"
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Investigadores únicos", f"{total_inv:,}")
    m2.metric("Departamentos con registros", f"{total_deptos:,}")
    m3.metric("Categoría predominante", categoria_top)

    st.info(resumen_issue_19(df_anio))

    if "NME_DEPARTAMENTO_RES_PR" not in df_anio.columns:
        st.error("No existe una columna de departamento usable para construir el mapa.")
    else:
        st.plotly_chart(
            figura_mapa_departamentos(df_anio),
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            figura_distribucion_categoria(df_anio),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            figura_distribucion_genero(df_anio),
            use_container_width=True
        )

    st.markdown("#### Top departamentos")
    tabla_deptos = tabla_top_departamentos(df_anio, top_n=10)
    st.dataframe(
        formatear_tabla_departamentos(tabla_deptos),
        use_container_width=True,
        hide_index=True,
    )

elif seccion == "Issue 20 · Ranking de instituciones":
    st.subheader("Issue 20 — Ranking de instituciones")
    st.caption(
        "Ranking de instituciones por número de investigadores, con filtros por categoría y área."
    )

    if "INST_FILIA" not in df_anio.columns:
        st.error("No existe una columna de institución usable para construir el ranking.")
        st.stop()

    df_filtrado = filtrar_instituciones(
    df_anio,
    categoria=categoria_sel,
    area=area_sel,
    )

    ranking_df = ranking_instituciones(df_filtrado, top_n=top_n)
    universo_inst = expandir_instituciones(df_filtrado)
    total_instituciones = universo_inst["INST_FILIA"].nunique()

    top_inst_nombre = (
        ranking_df.iloc[0]["institucion"] if not ranking_df.empty else "No disponible"
    )

    met1, met2, met3 = st.columns(3)
    met1.metric("Instituciones en el universo filtrado", f"{total_instituciones:,}")
    met2.metric(
        "Investigadores únicos filtrados",
        f"{df_filtrado['ID_PERSONA_PR'].nunique():,}"
    )
    met3.metric(
        "Institución líder",
        top_inst_nombre[:28] + "..." if len(top_inst_nombre) > 28 else top_inst_nombre
    )

    st.info(resumen_issue_20(ranking_df, anio_sel))

    st.dataframe(
        formatear_tabla_ranking(ranking_df),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.plotly_chart(
        figura_ranking_instituciones(ranking_df),
        use_container_width=True
    )

    with st.expander("Ver tabla de ranking", expanded=False):
        st.dataframe(
            formatear_tabla_ranking(ranking_df),
            use_container_width=True,
            hide_index=True,
            height=420,
        )