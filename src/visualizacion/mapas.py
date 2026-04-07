from __future__ import annotations

import unicodedata

import pandas as pd
import plotly.express as px

COORDENADAS_DEPARTAMENTOS: dict[str, tuple[float, float]] = {
    "AMAZONAS": (-1.0, -71.9),
    "ANTIOQUIA": (6.2442, -75.5812),
    "ARAUCA": (7.0667, -70.7500),
    "ATLANTICO": (10.9685, -74.7813),
    "BOGOTA": (4.7110, -74.0721),
    "BOLIVAR": (9.1000, -74.5000),
    "BOYACA": (5.5353, -73.3678),
    "CALDAS": (5.0703, -75.5138),
    "CAQUETA": (1.6140, -75.6062),
    "CASANARE": (5.3333, -71.3500),
    "CAUCA": (2.4448, -76.6147),
    "CESAR": (9.3373, -73.6536),
    "CHOCO": (5.6942, -76.6545),
    "CORDOBA": (8.7479, -75.8814),
    "CUNDINAMARCA": (4.7110, -74.0721),
    "GUAINIA": (3.8667, -67.9167),
    "GUAVIARE": (2.5667, -72.6500),
    "HUILA": (2.9273, -75.2819),
    "LA GUAJIRA": (11.5447, -72.9072),
    "MAGDALENA": (10.4631, -74.2271),
    "META": (4.1420, -73.6266),
    "NARINO": (1.2136, -77.2811),
    "NORTE DE SANTANDER": (7.8939, -72.5078),
    "PUTUMAYO": (0.4353, -76.6000),
    "QUINDIO": (4.5339, -75.6811),
    "RISARALDA": (4.8133, -75.6961),
    "SAN ANDRES": (12.5847, -81.7006),
    "SANTANDER": (6.6437, -73.6536),
    "SUCRE": (9.3047, -75.3978),
    "TOLIMA": (4.4389, -75.2322),
    "VALLE DEL CAUCA": (3.4372, -76.5225),
    "VAUPES": (0.2167, -70.2333),
    "VICHADA": (4.4233, -69.2878),
}

REEMPLAZOS_DEPARTAMENTO = {
    "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
    "SAN ANDRES Y PROVIDENCIA": "SAN ANDRES",
    "BOGOTA D.C.": "BOGOTA",
    "DISTRITO CAPITAL DE BOGOTA": "BOGOTA",
    "VALLE": "VALLE DEL CAUCA",
}


def normalizar_texto(texto: str | None) -> str:
    if texto is None or pd.isna(texto):
        return ""

    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = " ".join(texto.split())
    return texto


def preparar_mapa_departamentos(
    df: pd.DataFrame,
    columna_departamento: str = "NME_DEPARTAMENTO_RES_PR",
    columna_id: str = "ID_PERSONA_PR",
) -> pd.DataFrame:
    base = df[[columna_departamento, columna_id]].copy()
    base = base.dropna(subset=[columna_departamento, columna_id])

    base["departamento"] = base[columna_departamento].apply(normalizar_texto)
    base["departamento"] = base["departamento"].replace(REEMPLAZOS_DEPARTAMENTO)

    conteo = (
        base.groupby("departamento")[columna_id]
        .nunique()
        .reset_index(name="n_investigadores")
    )

    conteo["lat"] = conteo["departamento"].map(
        lambda x: COORDENADAS_DEPARTAMENTOS.get(x, (None, None))[0]
    )
    conteo["lon"] = conteo["departamento"].map(
        lambda x: COORDENADAS_DEPARTAMENTOS.get(x, (None, None))[1]
    )

    conteo = conteo.dropna(subset=["lat", "lon"]).sort_values(
        "n_investigadores", ascending=False
    )
    return conteo


def figura_mapa_departamentos(df: pd.DataFrame):
    mapa_df = preparar_mapa_departamentos(df)

    if mapa_df.empty:
        fig = px.scatter_geo()
        fig.update_layout(title="No hay datos suficientes para construir el mapa.")
        return fig

    fig = px.scatter_geo(
        mapa_df,
        lat="lat",
        lon="lon",
        size="n_investigadores",
        color="n_investigadores",
        hover_name="departamento",
        hover_data={
            "lat": False,
            "lon": False,
            "n_investigadores": ":,",
        },
        projection="mercator",
        title="Investigadores únicos por departamento",
        labels={"n_investigadores": "Investigadores"},
        size_max=60,
    )

    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1.0, color="white"))
    )

    fig.update_geos(
        center=dict(lat=4.5, lon=-73.5),
        projection_scale=7.2,
        lataxis_range=[-5, 14],
        lonaxis_range=[-82, -66],
        showcountries=True,
        countrycolor="gray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="rgb(242, 242, 242)",
        showocean=True,
        oceancolor="rgb(230, 240, 255)",
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        height=850,
        font=dict(size=14),
        title_font=dict(size=22),
        coloraxis_colorbar=dict(title="Investigadores"),
    )
    return fig


def tabla_top_departamentos(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    mapa_df = preparar_mapa_departamentos(df)

    if mapa_df.empty:
        return pd.DataFrame(
            columns=["Ranking", "Departamento", "Investigadores", "% del total"]
        )

    total = mapa_df["n_investigadores"].sum()

    salida = mapa_df.head(top_n).copy()
    salida["% del total"] = (salida["n_investigadores"] / total * 100).round(2)
    salida.insert(0, "Ranking", range(1, len(salida) + 1))

    salida = salida.rename(
        columns={
            "departamento": "Departamento",
            "n_investigadores": "Investigadores",
        }
    )

    return salida[["Ranking", "Departamento", "Investigadores", "% del total"]]