from __future__ import annotations

import pandas as pd
import plotly.express as px

COLUMNAS_AREA_CANDIDATAS = [
    "NME_GRAN_AREA_PR",
    "NME_AREA_PR",
    "NME_ESP_AREA_PR",
]


def obtener_columna_area(df: pd.DataFrame) -> str | None:
    for col in COLUMNAS_AREA_CANDIDATAS:
        if col in df.columns:
            return col
    return None


def expandir_instituciones(
    df: pd.DataFrame,
    columna_institucion: str = "INST_FILIA",
    columna_id: str = "ID_PERSONA_PR",
    columna_anio: str = "ANO_CONVO",
) -> pd.DataFrame:
    base = df.copy()

    if columna_institucion not in base.columns:
        raise KeyError(f"No existe la columna '{columna_institucion}' en el DataFrame.")

    base = base.dropna(subset=[columna_institucion, columna_id])

    base[columna_institucion] = (
        base[columna_institucion]
        .astype(str)
        .str.split("|")
    )

    base = base.explode(columna_institucion)

    base[columna_institucion] = (
        base[columna_institucion]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    base = base[base[columna_institucion] != ""]

    columnas_dedup = [columna_id, columna_institucion]
    if columna_anio in base.columns:
        columnas_dedup.append(columna_anio)

    base = base.drop_duplicates(subset=columnas_dedup)
    return base


def filtrar_instituciones(
    df: pd.DataFrame,
    categoria: str | None = None,
    area: str | None = None,
    columna_categoria: str = "NME_CLASIFICACION_PR",
) -> pd.DataFrame:
    base = df.copy()

    if categoria and categoria != "Todas":
        base = base[base[columna_categoria] == categoria]

    columna_area = obtener_columna_area(base)
    if area and area != "Todas" and columna_area is not None:
        base = base[base[columna_area] == area]

    return base


def ranking_instituciones(
    df: pd.DataFrame,
    top_n: int = 15,
    columna_institucion: str = "INST_FILIA",
    columna_id: str = "ID_PERSONA_PR",
) -> pd.DataFrame:
    base = expandir_instituciones(
        df,
        columna_institucion=columna_institucion,
        columna_id=columna_id,
    )

    ranking = (
        base.groupby(columna_institucion)[columna_id]
        .nunique()
        .reset_index(name="n_investigadores")
        .sort_values("n_investigadores", ascending=False)
        .head(top_n)
        .rename(columns={columna_institucion: "institucion"})
    )

    ranking.insert(0, "ranking", range(1, len(ranking) + 1))
    return ranking


def figura_ranking_instituciones(ranking_df: pd.DataFrame):
    if ranking_df.empty:
        fig = px.bar()
        fig.update_layout(title="No hay datos suficientes para construir el ranking.")
        return fig

    plot_df = ranking_df.copy()
    plot_df["institucion_corta"] = plot_df["institucion"].apply(
        lambda x: x[:32] + "..." if len(x) > 32 else x
    )

    plot_df = plot_df.sort_values("n_investigadores", ascending=True)

    fig = px.bar(
        plot_df,
        x="n_investigadores",
        y="institucion_corta",
        orientation="h",
        text="n_investigadores",
        title="Ranking de instituciones por número de investigadores",
        labels={
            "n_investigadores": "Investigadores únicos",
            "institucion_corta": "Institución",
        },
        hover_name="institucion",
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        margin=dict(l=10, r=20, t=60, b=10),
        height=max(760, 42 * len(plot_df)),
        font=dict(size=14),
        title_font=dict(size=20),
    )
    fig.update_xaxes(tickfont=dict(size=12))
    fig.update_yaxes(tickfont=dict(size=12), automargin=True)

    return fig