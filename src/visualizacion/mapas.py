"""
Visualizaciones geograficas — investigadores MinCiencias

Genera mapas interactivos con folium mostrando la distribucion
territorial de investigadores reconocidos por convocatoria.
"""

from __future__ import annotations

import folium
import pandas as pd
from folium.plugins import MarkerCluster

# Coordenadas aproximadas de capitales de departamento colombianas
COORDENADAS_DEPARTAMENTOS: dict[str, tuple[float, float]] = {
    "AMAZONAS": (-1.0, -71.9),
    "ANTIOQUIA": (6.2442, -75.5812),
    "ARAUCA": (7.0667, -70.7500),
    "ATLANTICO": (10.9685, -74.7813),
    "BOGOTA": (4.7110, -74.0721),
    "BOLIVAR": (9.1, -74.5),
    "BOYACA": (5.5353, -73.3678),
    "CALDAS": (5.0703, -75.5138),
    "CAQUETA": (1.614, -75.6062),
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
    "PUTUMAYO": (0.4353, -76.6),
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


def _normalizar_depto(nombre: str | None) -> str:
    """Normaliza el nombre del departamento para busqueda en el diccionario."""
    if pd.isna(nombre) or nombre is None:
        return ""
    s = str(nombre).upper().strip()
    s = s.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    s = s.replace("\u00c1", "A").replace("\u00c9", "E").replace("\u00cd", "I")
    s = s.replace("\u00d3", "O").replace("\u00da", "U")
    return s


def mapa_investigadores_por_depto(
    df: pd.DataFrame,
    anio: int | None = None,
    columna_depto: str = "NME_DEPARTAMENTO_RES_PR",
) -> folium.Map:
    """
    Mapa de burbujas: numero de investigadores por departamento.

    Parameters
    ----------
    df       : DataFrame consolidado de investigadores
    anio     : filtrar por año (None = todos)
    columna_depto : columna con el nombre del departamento

    Returns
    -------
    m : objeto folium.Map listo para renderizar en Streamlit
    """
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio].copy()

    conteo = (
        df.groupby(columna_depto)["ID_PERSONA_PR"]
        .count()
        .reset_index()
        .rename(columns={columna_depto: "departamento", "ID_PERSONA_PR": "n"})
    )
    conteo["depto_key"] = conteo["departamento"].apply(_normalizar_depto)

    m = folium.Map(location=[4.5, -74.0], zoom_start=5, tiles="CartoDB positron")

    max_n = conteo["n"].max() if len(conteo) > 0 else 1

    for _, row in conteo.iterrows():
        coords = COORDENADAS_DEPARTAMENTOS.get(row["depto_key"])
        if coords is None:
            continue
        radio = 5 + (row["n"] / max_n) * 30
        folium.CircleMarker(
            location=coords,
            radius=radio,
            color="#1a6faf",
            fill=True,
            fill_color="#1a6faf",
            fill_opacity=0.6,
            tooltip=f"{row['departamento']}: {row['n']:,} investigadores",
            popup=folium.Popup(
                f"<b>{row['departamento']}</b><br>{row['n']:,} investigadores",
                max_width=200,
            ),
        ).add_to(m)

    return m


def mapa_concentracion_territorial(
    df: pd.DataFrame,
    anio: int | None = None,
) -> folium.Map:
    """
    Mapa de calor (choropleth por cuartiles) de concentracion departamental.
    Distingue entre las 3 principales ciudades (Bogota, Medellin, Cali)
    y el resto del pais.
    """
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio].copy()

    total = len(df)
    conteo = (
        df.groupby("NME_DEPARTAMENTO_RES_PR")["ID_PERSONA_PR"]
        .count()
        .reset_index()
        .rename(columns={"NME_DEPARTAMENTO_RES_PR": "departamento", "ID_PERSONA_PR": "n"})
    )
    conteo["pct"] = (conteo["n"] / total * 100).round(2)
    conteo["depto_key"] = conteo["departamento"].apply(_normalizar_depto)

    m = folium.Map(location=[4.5, -74.0], zoom_start=5, tiles="CartoDB positron")

    principales = {"BOGOTA", "ANTIOQUIA", "VALLE DEL CAUCA"}

    for _, row in conteo.iterrows():
        coords = COORDENADAS_DEPARTAMENTOS.get(row["depto_key"])
        if coords is None:
            continue

        color = "#c0392b" if row["depto_key"] in principales else "#2980b9"
        radio = 4 + (row["pct"] / conteo["pct"].max()) * 28

        folium.CircleMarker(
            location=coords,
            radius=radio,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.65,
            tooltip=f"{row['departamento']}: {row['pct']}% ({row['n']:,})",
            popup=folium.Popup(
                f"<b>{row['departamento']}</b><br>"
                f"{row['n']:,} investigadores ({row['pct']}% del total)",
                max_width=220,
            ),
        ).add_to(m)

    # Leyenda
    leyenda = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:10px;border-radius:8px;
                border:1px solid #ccc;font-size:12px;">
        <b>Concentracion territorial</b><br>
        <span style="color:#c0392b;">&#9679;</span> Grandes centros urbanos<br>
        <span style="color:#2980b9;">&#9679;</span> Otros departamentos
    </div>
    """
    m.get_root().html.add_child(folium.Element(leyenda))
    return m
