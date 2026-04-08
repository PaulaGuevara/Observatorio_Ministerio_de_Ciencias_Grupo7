"""
Graficos de distribucion y analisis exploratorio — Sprint 3

Funciones que retornan figuras Plotly para embeber en el dashboard Streamlit.
Cubren: categoria, genero, edad, area OCDE, evolucion temporal y retencion.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Paleta institucional
COLORES_CATEGORIA = {
    "Investigador Junior": "#3498db",
    "Investigador Asociado": "#2ecc71",
    "Investigador Sénior": "#e67e22",
    "Investigador Emérito": "#9b59b6",
}
COLORES_GENERO = {"Masculino": "#2980b9", "Femenino": "#e74c3c"}
COLORES_ANIO = {2017: "#1abc9c", 2019: "#f39c12", 2021: "#8e44ad"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _limpiar_anio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ANO_CONVO"] = pd.to_datetime(df["ANO_CONVO"], dayfirst=True, errors="coerce").dt.year
    return df


# ---------------------------------------------------------------------------
# Distribucion por categoria
# ---------------------------------------------------------------------------

def figura_categoria_anio(df: pd.DataFrame) -> go.Figure:
    """Barras agrupadas: numero de investigadores por categoria y año."""
    df = _limpiar_anio(df)
    conteo = (
        df.groupby(["ANO_CONVO", "NME_CLASIFICACION_PR"])["ID_PERSONA_PR"]
        .count()
        .reset_index()
        .rename(columns={"ANO_CONVO": "Año", "NME_CLASIFICACION_PR": "Categoría", "ID_PERSONA_PR": "n"})
    )
    conteo["Año"] = conteo["Año"].astype(str)
    fig = px.bar(
        conteo,
        x="Categoría",
        y="n",
        color="Año",
        barmode="group",
        text="n",
        title="Investigadores por categoría y convocatoria",
        labels={"n": "Investigadores", "Categoría": "Categoría"},
        color_discrete_map={str(k): v for k, v in COLORES_ANIO.items()},
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(
        xaxis_tickangle=-20,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=60),
    )
    return fig


def figura_evolucion_categoria(df: pd.DataFrame) -> go.Figure:
    """Lineas de evolucion temporal por categoria."""
    df = _limpiar_anio(df)
    conteo = (
        df.groupby(["ANO_CONVO", "NME_CLASIFICACION_PR"])["ID_PERSONA_PR"]
        .count()
        .reset_index()
        .rename(columns={"ANO_CONVO": "Año", "NME_CLASIFICACION_PR": "Categoría", "ID_PERSONA_PR": "n"})
    )
    fig = px.line(
        conteo,
        x="Año",
        y="n",
        color="Categoría",
        markers=True,
        title="Evolución de investigadores por categoría (2017–2021)",
        labels={"n": "Investigadores"},
        color_discrete_map=COLORES_CATEGORIA,
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=50))
    fig.update_xaxes(tickvals=[2017, 2019, 2021])
    return fig


# ---------------------------------------------------------------------------
# Distribucion por genero
# ---------------------------------------------------------------------------

def figura_genero_anio(df: pd.DataFrame) -> go.Figure:
    """Barras apiladas al 100 % por genero y año."""
    df = _limpiar_anio(df)
    conteo = (
        df[df["NME_GENERO_PR"].isin(["Masculino", "Femenino"])]
        .groupby(["ANO_CONVO", "NME_GENERO_PR"])["ID_PERSONA_PR"]
        .count()
        .reset_index()
        .rename(columns={"ANO_CONVO": "Año", "NME_GENERO_PR": "Género", "ID_PERSONA_PR": "n"})
    )
    totales = conteo.groupby("Año")["n"].transform("sum")
    conteo["pct"] = (conteo["n"] / totales * 100).round(1)
    conteo["Año"] = conteo["Año"].astype(str)

    fig = px.bar(
        conteo,
        x="Año",
        y="pct",
        color="Género",
        barmode="relative",
        text=conteo["pct"].apply(lambda x: f"{x}%"),
        title="Distribución de género por convocatoria (%)",
        labels={"pct": "Porcentaje (%)", "Año": "Convocatoria"},
        color_discrete_map=COLORES_GENERO,
    )
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(
        yaxis=dict(range=[0, 100], ticksuffix="%"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50),
    )
    return fig


def figura_genero_area(df: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """Heatmap % femenino por gran area OCDE y año."""
    df = _limpiar_anio(df)
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio]
    df = df[df["NME_GENERO_PR"].isin(["Masculino", "Femenino"])]

    pivot = (
        df.groupby(["NME_GRAN_AREA_PR", "ANO_CONVO", "NME_GENERO_PR"])["ID_PERSONA_PR"]
        .count()
        .unstack("NME_GENERO_PR", fill_value=0)
        .reset_index()
    )
    if "Femenino" not in pivot.columns:
        pivot["Femenino"] = 0
    pivot["pct_fem"] = (pivot["Femenino"] / (pivot["Femenino"] + pivot.get("Masculino", 0)) * 100).round(1)

    tabla = pivot.pivot_table(values="pct_fem", index="NME_GRAN_AREA_PR", columns="ANO_CONVO")
    tabla.columns = [str(c) for c in tabla.columns]

    fig = px.imshow(
        tabla,
        text_auto=".1f",
        color_continuous_scale="RdBu",
        zmin=0,
        zmax=100,
        aspect="auto",
        title="% Investigadoras por gran área OCDE y convocatoria",
        labels=dict(color="% Femenino", x="Año", y="Gran Área"),
    )
    fig.update_layout(
        coloraxis_colorbar=dict(ticksuffix="%"),
        margin=dict(t=60, l=220),
    )
    return fig


# ---------------------------------------------------------------------------
# Distribucion de edad
# ---------------------------------------------------------------------------

def figura_edad_categoria(df: pd.DataFrame, anio: int | None = None) -> go.Figure:
    """Box plots de edad por categoria (violin + box)."""
    df = _limpiar_anio(df)
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio]
    df = df.dropna(subset=["EDAD_ANOS_PR", "NME_CLASIFICACION_PR"])
    df["EDAD_ANOS_PR"] = pd.to_numeric(df["EDAD_ANOS_PR"], errors="coerce")
    df = df[df["EDAD_ANOS_PR"].between(20, 90)]

    orden = ["Investigador Junior", "Investigador Asociado", "Investigador Sénior", "Investigador Emérito"]
    df["NME_CLASIFICACION_PR"] = pd.Categorical(
        df["NME_CLASIFICACION_PR"], categories=orden, ordered=True
    )
    df = df.sort_values("NME_CLASIFICACION_PR")

    fig = px.violin(
        df,
        x="NME_CLASIFICACION_PR",
        y="EDAD_ANOS_PR",
        color="NME_CLASIFICACION_PR",
        box=True,
        points=False,
        title="Distribución de edad por categoría",
        labels={"EDAD_ANOS_PR": "Edad (años)", "NME_CLASIFICACION_PR": "Categoría"},
        color_discrete_map=COLORES_CATEGORIA,
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickangle=-15,
        margin=dict(t=50),
    )
    return fig


# ---------------------------------------------------------------------------
# Top instituciones
# ---------------------------------------------------------------------------

def figura_top_instituciones(
    df: pd.DataFrame,
    n: int = 15,
    anio: int | None = None,
) -> go.Figure:
    """Barras horizontales con las N instituciones con mas investigadores."""
    df = _limpiar_anio(df)
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio]
    df = df.dropna(subset=["INST_FILIA"])

    conteo = (
        df["INST_FILIA"].str.upper().value_counts().head(n).reset_index()
    )
    conteo.columns = ["Institución", "n"]
    # Truncar nombres largos
    conteo["Institución"] = conteo["Institución"].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
    conteo = conteo.sort_values("n")

    fig = px.bar(
        conteo,
        x="n",
        y="Institución",
        orientation="h",
        text="n",
        title=f"Top {n} instituciones por número de investigadores",
        labels={"n": "Investigadores", "Institución": ""},
        color="n",
        color_continuous_scale="Blues",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, l=10),
        height=max(350, n * 28),
    )
    return fig


# ---------------------------------------------------------------------------
# Retencion longitudinal
# ---------------------------------------------------------------------------

def figura_retencion(df: pd.DataFrame) -> go.Figure:
    """
    Sankey de retencion: investigadores que aparecen en 1, 2 o 3 convocatorias.
    """
    df = _limpiar_anio(df)
    apariciones = df.groupby("ID_PERSONA_PR")["ANO_CONVO"].nunique().value_counts().sort_index()

    etiquetas = [f"{k} convocatoria{'s' if k > 1 else ''}" for k in apariciones.index]
    valores = apariciones.values.tolist()
    colores = ["#3498db", "#2ecc71", "#e67e22"]

    fig = go.Figure(go.Bar(
        x=etiquetas,
        y=valores,
        text=valores,
        textposition="outside",
        marker_color=colores[: len(valores)],
    ))
    fig.update_layout(
        title="Retención longitudinal de investigadores",
        xaxis_title="Número de convocatorias en que aparece",
        yaxis_title="Investigadores (personas únicas)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50),
    )
    return fig


# ---------------------------------------------------------------------------
# KPIs resumidos
# ---------------------------------------------------------------------------

def calcular_kpis(df: pd.DataFrame) -> dict:
    """Calcula indicadores clave para el encabezado del dashboard."""
    df = _limpiar_anio(df)
    total = df["ID_PERSONA_PR"].nunique()
    total_registros = len(df)

    df_gen = df[df["NME_GENERO_PR"].isin(["Masculino", "Femenino"])]
    pct_fem = (
        (df_gen["NME_GENERO_PR"] == "Femenino").sum() / len(df_gen) * 100
        if len(df_gen) > 0 else 0
    )

    por_anio = df.groupby("ANO_CONVO")["ID_PERSONA_PR"].count().to_dict()
    instituciones = df["INST_FILIA"].nunique()
    municipios = df["NME_MUNICIPIO_RES_PR"].nunique()

    return {
        "total_investigadores_unicos": total,
        "total_registros": total_registros,
        "pct_femenino": round(pct_fem, 1),
        "por_anio": por_anio,
        "instituciones": instituciones,
        "municipios": municipios,
    }
