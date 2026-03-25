# -*- coding: utf-8 -*-
"""
streamlit_app.py

Tablero de control interactivo para el Observatorio de Ciencia, Tecnología e
Innovación — Investigadores Reconocidos Minciencias (Grupo 7).

Ejecución:
    streamlit run streamlit_app.py
"""

import pathlib
import sys

import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ingesta import cargar_consolidado  # noqa: E402
from Transformacion import transformar  # noqa: E402

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Observatorio Minciencias — Grupo 7",
    page_icon="🔬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Carga y transformación de datos (cacheado)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando datos…")
def cargar_datos() -> pd.DataFrame:
    df = cargar_consolidado()
    df = transformar(df)
    return df


# ---------------------------------------------------------------------------
# Sidebar — filtros
# ---------------------------------------------------------------------------

def sidebar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("🔎 Filtros")

    # Año de convocatoria
    anios = sorted(df["ANO_CONVO_INT"].dropna().unique().tolist())
    anios_sel = st.sidebar.multiselect(
        "Año de convocatoria",
        options=anios,
        default=anios,
    )

    # Género
    generos = sorted(df["NME_GENERO_PR"].dropna().unique().tolist())
    generos_sel = st.sidebar.multiselect(
        "Género",
        options=generos,
        default=generos,
    )

    # Gran área de conocimiento
    areas = sorted(df["NME_GRAN_AREA_PR"].dropna().unique().tolist())
    areas_sel = st.sidebar.multiselect(
        "Gran área de conocimiento",
        options=areas,
        default=areas,
    )

    # Aplicar filtros
    mascara = (
        df["ANO_CONVO_INT"].isin(anios_sel)
        & df["NME_GENERO_PR"].isin(generos_sel)
        & df["NME_GRAN_AREA_PR"].isin(areas_sel)
    )
    return df[mascara]


# ---------------------------------------------------------------------------
# Secciones del tablero
# ---------------------------------------------------------------------------

def seccion_resumen(df: pd.DataFrame) -> None:
    st.header("📊 Resumen general")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de registros", f"{len(df):,}")
    col2.metric(
        "Investigadores únicos",
        f"{df['ID_PERSONA_PR'].nunique():,}" if "ID_PERSONA_PR" in df.columns else "N/A",
    )
    col3.metric(
        "Convocatorias",
        f"{df['ANO_CONVO_INT'].nunique():,}" if "ANO_CONVO_INT" in df.columns else "N/A",
    )


def seccion_evolucion(df: pd.DataFrame) -> None:
    st.header("📈 Evolución por convocatoria")
    if "ANO_CONVO_INT" not in df.columns:
        st.warning("No se pudo determinar el año de convocatoria.")
        return
    conteo = (
        df.groupby("ANO_CONVO_INT")
        .size()
        .reset_index(name="Investigadores")
        .rename(columns={"ANO_CONVO_INT": "Año"})
    )
    fig = px.bar(
        conteo,
        x="Año",
        y="Investigadores",
        text_auto=True,
        title="Número de investigadores reconocidos por convocatoria",
        color="Investigadores",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_genero(df: pd.DataFrame) -> None:
    st.header("👥 Distribución por género")
    if "NME_GENERO_PR" not in df.columns:
        st.warning("Columna de género no disponible.")
        return
    conteo = df["NME_GENERO_PR"].value_counts().reset_index()
    conteo.columns = ["Género", "Cantidad"]
    fig = px.pie(
        conteo,
        names="Género",
        values="Cantidad",
        title="Distribución por género",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_areas(df: pd.DataFrame) -> None:
    st.header("🔬 Distribución por gran área de conocimiento")
    if "NME_GRAN_AREA_PR" not in df.columns:
        st.warning("Columna de área no disponible.")
        return
    conteo = (
        df["NME_GRAN_AREA_PR"]
        .value_counts()
        .reset_index()
    )
    conteo.columns = ["Gran Área", "Cantidad"]
    fig = px.bar(
        conteo,
        x="Cantidad",
        y="Gran Área",
        orientation="h",
        title="Investigadores por gran área OCDE",
        color="Cantidad",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_departamentos(df: pd.DataFrame) -> None:
    st.header("🗺️ Distribución por departamento de residencia")
    col = "NME_DEPARTAMENTO_RES_PR"
    if col not in df.columns:
        st.warning("Columna de departamento no disponible.")
        return
    top20 = df[col].value_counts().head(20).reset_index()
    top20.columns = ["Departamento", "Cantidad"]
    fig = px.bar(
        top20,
        x="Cantidad",
        y="Departamento",
        orientation="h",
        title="Top 20 departamentos de residencia",
        color="Cantidad",
        color_continuous_scale="Oranges",
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_nivel_formacion(df: pd.DataFrame) -> None:
    st.header("🎓 Nivel de formación")
    col = "NME_NIV_FORM_PR"
    if col not in df.columns:
        st.warning("Columna de nivel de formación no disponible.")
        return
    conteo = df[col].value_counts().reset_index()
    conteo.columns = ["Nivel", "Cantidad"]
    fig = px.bar(
        conteo,
        x="Nivel",
        y="Cantidad",
        text_auto=True,
        title="Distribución por nivel de formación",
        color="Cantidad",
        color_continuous_scale="Purples",
    )
    fig.update_xaxes(tickangle=30)
    st.plotly_chart(fig, use_container_width=True)


def seccion_datos_crudos(df: pd.DataFrame) -> None:
    with st.expander("🗃️ Ver datos (primeras 500 filas)"):
        st.dataframe(df.head(500))


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

def main() -> None:
    st.title("🔬 Observatorio de Ciencia, Tecnología e Innovación")
    st.caption(
        "Investigadores Reconocidos por Convocatoria — Minciencias — Grupo 7"
    )

    try:
        df_raw = cargar_datos()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    df = sidebar_filtros(df_raw)

    if df.empty:
        st.warning("No hay registros para los filtros seleccionados.")
        return

    seccion_resumen(df)

    col_izq, col_der = st.columns(2)
    with col_izq:
        seccion_evolucion(df)
    with col_der:
        seccion_genero(df)

    seccion_areas(df)
    seccion_departamentos(df)
    seccion_nivel_formacion(df)
    seccion_datos_crudos(df)


if __name__ == "__main__":
    main()
