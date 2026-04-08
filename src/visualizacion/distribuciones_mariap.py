from __future__ import annotations

import pandas as pd
import plotly.express as px

ORDEN_CATEGORIAS = [
    "Investigador Junior",
    "Investigador Asociado",
    "Investigador Sénior",
    "Investigador Senior",
    "Investigador Emérito",
    "Investigador Emerito",
]


def preparar_distribucion_categoria(
    df: pd.DataFrame,
    columna_categoria: str = "NME_CLASIFICACION_PR",
    columna_id: str = "ID_PERSONA_PR",
) -> pd.DataFrame:
    base = df[[columna_categoria, columna_id]].copy()
    base[columna_categoria] = base[columna_categoria].fillna("No registra")

    base = (
        base.groupby(columna_categoria)[columna_id]
        .nunique()
        .reset_index(name="n_investigadores")
    )

    presentes = [cat for cat in ORDEN_CATEGORIAS if cat in base[columna_categoria].tolist()]
    otros = [
        cat for cat in sorted(base[columna_categoria].tolist())
        if cat not in presentes
    ]
    orden = presentes + otros

    base[columna_categoria] = pd.Categorical(
        base[columna_categoria],
        categories=orden,
        ordered=True,
    )

    base = base.sort_values(columna_categoria)
    return base


def figura_distribucion_categoria(df: pd.DataFrame):
    base = preparar_distribucion_categoria(df)

    if base.empty:
        fig = px.bar()
        fig.update_layout(title="No hay datos de categoría para mostrar.")
        return fig

    total = base["n_investigadores"].sum()
    base["porcentaje"] = (base["n_investigadores"] / total * 100).round(2)
    base["texto"] = base["n_investigadores"].map(lambda x: f"{x:,}")

    fig = px.bar(
        base,
        x="NME_CLASIFICACION_PR",
        y="n_investigadores",
        text="texto",
        title="Distribución por categoría",
        labels={
            "NME_CLASIFICACION_PR": "Categoría",
            "n_investigadores": "Investigadores únicos",
        },
        hover_data={"porcentaje": ":.2f"},
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_tickangle=-10,
        margin=dict(l=10, r=10, t=60, b=20),
        height=520,
        font=dict(size=14),
        title_font=dict(size=20),
    )
    fig.update_xaxes(tickfont=dict(size=12))
    fig.update_yaxes(tickfont=dict(size=12))

    return fig


def preparar_distribucion_genero(
    df: pd.DataFrame,
    columna_genero: str = "NME_GENERO_PR",
    columna_id: str = "ID_PERSONA_PR",
) -> pd.DataFrame:
    base = df[[columna_genero, columna_id]].copy()
    base[columna_genero] = base[columna_genero].fillna("No registra")
    base[columna_genero] = base[columna_genero].replace({"": "No registra"})

    base = (
        base.groupby(columna_genero)[columna_id]
        .nunique()
        .reset_index(name="n_investigadores")
        .sort_values("n_investigadores", ascending=True)
    )

    total = base["n_investigadores"].sum()
    base["porcentaje"] = (base["n_investigadores"] / total * 100).round(2)
    base["texto"] = base.apply(
        lambda row: f"{row['n_investigadores']:,} ({row['porcentaje']:.1f}%)",
        axis=1,
    )
    return base


def figura_distribucion_genero(df: pd.DataFrame):
    base = preparar_distribucion_genero(df)

    if base.empty:
        fig = px.bar()
        fig.update_layout(title="No hay datos de género para mostrar.")
        return fig

    fig = px.bar(
        base,
        x="n_investigadores",
        y="NME_GENERO_PR",
        orientation="h",
        text="texto",
        title="Distribución por género",
        labels={
            "n_investigadores": "Investigadores únicos",
            "NME_GENERO_PR": "Género",
        },
        hover_data={"porcentaje": ":.2f"},
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        height=520,
        font=dict(size=14),
        title_font=dict(size=20),
    )
    fig.update_xaxes(tickfont=dict(size=12))
    fig.update_yaxes(tickfont=dict(size=12))

    return fig