from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

import dashboard_sprint_3 as sprint3


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
CONVOCATORIA_PRIORITY = {"2021": 3, "2019": 2, "2017": 1}


DEPT_COORDS = {
    "AMAZONAS": (-4.2153, -69.9406),
    "ANTIOQUIA": (6.2442, -75.5812),
    "ARAUCA": (7.0847, -70.7591),
    "ATLANTICO": (10.9685, -74.7813),
    "BOGOTA D C": (4.7110, -74.0721),
    "BOLIVAR": (10.3910, -75.4794),
    "BOYACA": (5.5353, -73.3678),
    "CALDAS": (5.0703, -75.5138),
    "CAQUETA": (1.6139, -75.6126),
    "CASANARE": (5.3489, -72.4005),
    "CAUCA": (2.4448, -76.6147),
    "CESAR": (10.4631, -73.2532),
    "CHOCO": (5.6947, -76.6611),
    "CORDOBA": (8.74798, -75.8814),
    "CUNDINAMARCA": (4.8133, -74.3540),
    "GUAINIA": (2.5729, -72.6459),
    "GUAVIARE": (2.5729, -72.6459),
    "HUILA": (2.9386, -75.2809),
    "LA GUAJIRA": (11.5444, -72.9072),
    "MAGDALENA": (11.2408, -74.1990),
    "META": (4.1420, -73.6266),
    "NARINO": (1.2136, -77.2811),
    "NORTE DE SANTANDER": (7.8891, -72.4967),
    "PUTUMAYO": (0.5051, -76.5008),
    "QUINDIO": (4.5339, -75.6811),
    "RISARALDA": (4.8143, -75.6946),
    "SAN ANDRES Y PROVIDENCIA": (12.5847, -81.7006),
    "SANTANDER": (7.1193, -73.1227),
    "SUCRE": (9.3047, -75.3978),
    "TOLIMA": (4.4389, -75.2322),
    "VALLE DEL CAUCA": (3.4516, -76.5320),
    "VAUPES": (0.8554, -70.8120),
    "VICHADA": (5.6930, -67.4916),
}


def normalize_text(value: str) -> str:
    mapping = {
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ü": "U",
        ",": " ",
        ".": " ",
    }
    text = (value or "").upper().strip()
    for old, new in mapping.items():
        text = text.replace(old, new)
    return " ".join(text.split())


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, encoding="latin-1", low_memory=False)


def build_unique_department_counter(df: pd.DataFrame) -> Counter[str]:
    latest_by_person: dict[str, tuple[int, str]] = {}
    for _, row in df.iterrows():
        department = (row.get("NME_DEPARTAMENTO_RES_PR") or "").strip()
        person_id = str(row.get("ID_PERSONA_PR") or "").strip()
        year = str(row.get("ANO_CONVO") or "").strip()[:4]
        if not department or not person_id:
            continue
        score = CONVOCATORIA_PRIORITY.get(year, 0)
        previous = latest_by_person.get(person_id)
        if previous is None or score > previous[0]:
            latest_by_person[person_id] = (score, department)
    return Counter(value[1] for value in latest_by_person.values())


def hhi_10000(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return sum(((count / total) ** 2) * 10000 for count in counter.values())


def concentration_label(value: float) -> str:
    if value < 1500:
        return "baja"
    if value < 2500:
        return "moderada"
    return "alta"


def sprint2_dataframe(counter: Counter[str]) -> pd.DataFrame:
    total = sum(counter.values())
    rows = []
    for dept, count in counter.items():
        pct = (count / total) * 100 if total else 0.0
        key = normalize_text(dept)
        lat_lon = DEPT_COORDS.get(key)
        rows.append(
            {
                "departamento": dept,
                "investigadores": count,
                "participacion_pct": pct,
                "lat": lat_lon[0] if lat_lon else None,
                "lon": lat_lon[1] if lat_lon else None,
            }
        )
    return pd.DataFrame(rows).sort_values("investigadores", ascending=False)


def render_sprint2_tab(df: pd.DataFrame) -> None:
    counter = build_unique_department_counter(df)
    table = sprint2_dataframe(counter)
    hhi = hhi_10000(counter)

    top_focus = table[table["departamento"].isin(["Bogotá, D. C.", "Antioquia", "Valle del Cauca"])].copy()
    focus_pct = float(top_focus["participacion_pct"].sum()) if not top_focus.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("HHI (0 a 10.000)", f"{hhi:.2f}")
    c2.metric("Nivel", concentration_label(hhi).title())
    c3.metric("Departamentos", len(counter))
    c4.metric("Bogotá + Antioquia + Valle", f"{focus_pct:.2f}%")

    st.subheader("Mapa territorial (Sprint 2)")
    map_df = table.dropna(subset=["lat", "lon"]).copy()
    if map_df.empty:
        st.warning("No se encontraron coordenadas para construir el mapa.")
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_radius="investigadores * 35",
            get_fill_color="[15, 118, 110, 170]",
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=4.6, longitude=-74.1, zoom=4.6)
        tooltip = {
            "html": "<b>{departamento}</b><br/>Investigadores: {investigadores}<br/>Participación: {participacion_pct}%",
            "style": {"backgroundColor": "#1f2937", "color": "white"},
        }
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

    st.subheader("Top 10 departamentos")
    st.dataframe(table[["departamento", "investigadores", "participacion_pct"]].head(10), use_container_width=True)


def render_sprint3_tab() -> None:
    c1, c2 = st.columns(2)
    with c1:
        min_shared = st.slider("Mínimo de investigadores por arista", min_value=1, max_value=15, value=2)
    with c2:
        max_nodes = st.slider("Máximo de nodos en pantalla", min_value=30, max_value=500, value=160, step=10)

    graph, meta = sprint3.build_graph(min_shared=min_shared)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Investigadores con afiliación", f"{meta['people_with_aff']:,}".replace(",", "."))
    m2.metric("Investigadores con co-filiación", f"{meta['people_multi_aff']:,}".replace(",", "."))
    m3.metric("Instituciones (nodos)", graph.number_of_nodes())
    m4.metric("Conexiones (aristas)", graph.number_of_edges())

    density = nx.density(graph) if graph.number_of_nodes() > 1 else 0.0
    st.write(f"Densidad de red: **{density:.6f}**")

    if graph.number_of_nodes() == 0:
        st.warning("No hay nodos para visualizar con los filtros actuales.")
        return

    html = sprint3.build_pyvis_html(graph, max_nodes=max_nodes)
    components.html(html, height=790, scrolling=True)

    st.subheader("Top instituciones más conectadas")
    st.dataframe(sprint3.top_institutions(graph), use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Observatorio Minciencias", page_icon="📊", layout="wide")
    st.title("Observatorio Minciencias - Dashboard unificado")

    tab_s2, tab_s3 = st.tabs([
        "Sprint 2 - HHI y concentración territorial",
        "Sprint 3 - Co-filiación interactiva",
    ])

    data = load_data()

    with tab_s2:
        render_sprint2_tab(data)

    with tab_s3:
        render_sprint3_tab()


if __name__ == "__main__":
    main()