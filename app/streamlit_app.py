"""
Dashboard interactivo — Observatorio MinCiencias
Investigadores reconocidos 2017 · 2019 · 2021

Paginas:
    1. Resumen       — KPIs y metricas globales
    2. Territorio    — Mapa interactivo por departamento
    3. Distribuciones— Categoria, genero, edad, top instituciones
    4. Redes         — Grafo de co-filiacion institucional

Uso:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"

# ---------------------------------------------------------------------------
# Configuracion de pagina
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Observatorio MinCiencias · Ustadística",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS minimo
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .kpi-card {
        background: #f0f4fa;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        border-left: 5px solid #1a6faf;
    }
    .kpi-valor { font-size: 2rem; font-weight: 700; color: #1a6faf; }
    .kpi-label { font-size: 0.85rem; color: #555; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Carga de datos (cacheada)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df["ANO_CONVO"] = pd.to_datetime(df["ANO_CONVO"], dayfirst=True, errors="coerce").dt.year
    df["INST_FILIA"] = df["INST_FILIA"].fillna("Sin institución").str.strip().str.upper()
    df["NME_GENERO_PR"] = df["NME_GENERO_PR"].fillna("No registra")
    return df


df_global = cargar_datos()
anios_disponibles = sorted(df_global["ANO_CONVO"].dropna().unique().astype(int).tolist())

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Observatorio MinCiencias")
    st.caption("Ustadística · Universidad Santo Tomás · 2026-I")
    st.divider()

    pagina = st.radio(
        "Navegacion",
        ["📊 Resumen", "🗺️ Territorio", "📈 Distribuciones", "🕸️ Redes"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Filtros globales**")

    anio_sel = st.selectbox(
        "Convocatoria",
        ["Todas"] + anios_disponibles,
        index=0,
    )
    anio_filtro: int | None = None if anio_sel == "Todas" else int(anio_sel)

    df = df_global.copy() if anio_filtro is None else df_global[df_global["ANO_CONVO"] == anio_filtro].copy()

    generos = ["Todos"] + sorted(df_global["NME_GENERO_PR"].unique().tolist())
    genero_sel = st.selectbox("Género", generos, index=0)
    if genero_sel != "Todos":
        df = df[df["NME_GENERO_PR"] == genero_sel]

    st.caption(f"Registros visibles: **{len(df):,}**")


# ===========================================================================
# PAGINA 1 — RESUMEN
# ===========================================================================

if pagina == "📊 Resumen":
    st.title("📊 Resumen general")
    st.markdown(
        "Investigadores reconocidos por MinCiencias en las convocatorias "
        "**2017, 2019 y 2021**."
    )

    from src.visualizacion.distribuciones import calcular_kpis
    kpis = calcular_kpis(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-valor">{kpis['total_investigadores_unicos']:,}</div>
            <div class="kpi-label">Investigadores únicos</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-valor">{kpis['total_registros']:,}</div>
            <div class="kpi-label">Registros totales</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-valor">{kpis['pct_femenino']}%</div>
            <div class="kpi-label">Investigadoras</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-valor">{kpis['instituciones']:,}</div>
            <div class="kpi-label">Instituciones</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-valor">{kpis['municipios']:,}</div>
            <div class="kpi-label">Municipios</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    from src.visualizacion.distribuciones import (
        figura_evolucion_categoria,
        figura_genero_anio,
        figura_retencion,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(figura_evolucion_categoria(df), use_container_width=True)
    with col_b:
        st.plotly_chart(figura_genero_anio(df), use_container_width=True)

    st.plotly_chart(figura_retencion(df_global), use_container_width=True)

    st.divider()
    st.markdown("#### Preguntas de investigacion")
    for pregunta in [
        "¿Cuál es la tasa de retención de investigadores reconocidos entre convocatorias sucesivas?",
        "¿Qué instituciones concentran la mayor producción de investigadores Senior y Emérito?",
        "¿Existe segregación territorial en el reconocimiento de investigadores por fuera de las tres principales ciudades?",
        "¿La representación de mujeres investigadoras ha mejorado significativamente entre 2017 y 2021 en áreas STEM?",
    ]:
        st.markdown(f"- {pregunta}")


# ===========================================================================
# PAGINA 2 — TERRITORIO
# ===========================================================================

elif pagina == "🗺️ Territorio":
    st.title("🗺️ Distribución territorial")

    tipo_mapa = st.radio(
        "Tipo de mapa",
        ["Densidad por departamento", "Concentracion vs. resto del pais"],
        horizontal=True,
    )

    from src.visualizacion.mapas import mapa_investigadores_por_depto, mapa_concentracion_territorial

    try:
        from streamlit_folium import st_folium  # type: ignore[import]

        if tipo_mapa == "Densidad por departamento":
            m = mapa_investigadores_por_depto(df, anio=anio_filtro)
        else:
            m = mapa_concentracion_territorial(df, anio=anio_filtro)

        st_folium(m, width=None, height=520, returned_objects=[])

    except ImportError:
        st.info(
            "Instala `streamlit-folium` para el mapa interactivo:  \n"
            "`pip install streamlit-folium`  \n"
            "Mostrando tabla de conteo como alternativa."
        )
        conteo = (
            df.groupby("NME_DEPARTAMENTO_RES_PR")["ID_PERSONA_PR"]
            .count()
            .reset_index()
            .rename(columns={
                "NME_DEPARTAMENTO_RES_PR": "Departamento",
                "ID_PERSONA_PR": "Investigadores",
            })
            .sort_values("Investigadores", ascending=False)
        )
        st.dataframe(conteo, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### Top 10 departamentos")
    top_deptos = (
        df.groupby("NME_DEPARTAMENTO_RES_PR")["ID_PERSONA_PR"]
        .count()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={
            "NME_DEPARTAMENTO_RES_PR": "Departamento",
            "ID_PERSONA_PR": "Investigadores",
        })
    )
    top_deptos["% del total"] = (
        top_deptos["Investigadores"] / len(df) * 100
    ).round(1).astype(str) + "%"
    st.dataframe(top_deptos, use_container_width=True, hide_index=True)


# ===========================================================================
# PAGINA 3 — DISTRIBUCIONES
# ===========================================================================

elif pagina == "📈 Distribuciones":
    st.title("📈 Análisis de distribuciones")

    from src.visualizacion.distribuciones import (
        figura_categoria_anio,
        figura_genero_area,
        figura_edad_categoria,
        figura_top_instituciones,
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Categoría", "Género × Área", "Edad", "Top Instituciones"])

    with tab1:
        st.plotly_chart(figura_categoria_anio(df), use_container_width=True)

    with tab2:
        st.plotly_chart(figura_genero_area(df, anio=anio_filtro), use_container_width=True)

    with tab3:
        st.plotly_chart(figura_edad_categoria(df, anio=anio_filtro), use_container_width=True)

    with tab4:
        n_inst = st.slider("Número de instituciones", 5, 30, 15)
        st.plotly_chart(
            figura_top_instituciones(df, n=n_inst, anio=anio_filtro),
            use_container_width=True,
        )

    st.divider()
    with st.expander("Ver tabla de datos filtrados (primeros 500 registros)"):
        cols_mostrar = [
            "ID_PERSONA_PR", "ANO_CONVO", "NME_CLASIFICACION_PR",
            "NME_GENERO_PR", "EDAD_ANOS_PR", "NME_GRAN_AREA_PR",
            "NME_DEPARTAMENTO_RES_PR", "INST_FILIA",
        ]
        st.dataframe(
            df[[c for c in cols_mostrar if c in df.columns]].head(500),
            use_container_width=True,
            hide_index=True,
        )


# ===========================================================================
# PAGINA 4 — REDES
# ===========================================================================

elif pagina == "🕸️ Redes":
    st.title("🕸️ Red de co-filiación institucional")
    st.markdown(
        "Dos instituciones están conectadas si el mismo investigador aparece en ambas "
        "a lo largo de las convocatorias. El tamaño del nodo refleja el número de "
        "investigadores registrados. El color indica la **comunidad** detectada."
    )

    with st.sidebar:
        st.divider()
        st.markdown("**Configuracion de la red**")
        top_n = st.slider("Top N instituciones", 10, 80, 40, step=5)
        min_grado = st.slider("Grado mínimo de conexión", 1, 10, 1)
        fisica_on = st.toggle("Simulacion de fuerzas", value=True)

    from src.modelo.redes import (
        cargar_datos as cargar_red,
        construir_grafo_cofiliacion,
        calcular_metricas,
        tabla_nodos,
    )
    from src.visualizacion.redes import grafo_a_html_filtrado

    with st.spinner("Construyendo grafo..."):
        df_red = cargar_red(anio=anio_filtro)
        G = construir_grafo_cofiliacion(df_red, top_n=top_n)
        metricas = calcular_metricas(G)

    # KPIs de la red
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Nodos", metricas.get("n_nodos", 0))
    m2.metric("Arcos", metricas.get("n_arcos", 0))
    m3.metric("Densidad", metricas.get("densidad", 0))
    m4.metric("Comunidades", metricas.get("n_comunidades", 0))
    m5.metric("Componentes", metricas.get("componentes_conectados", 0))

    st.divider()

    with st.spinner("Renderizando grafo..."):
        html_grafo = grafo_a_html_filtrado(G, min_grado=min_grado, altura="580px")

    st_html(html_grafo, height=600, scrolling=False)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Centralidad de grado (top 10)")
        if metricas.get("top_degree"):
            df_deg = pd.DataFrame(metricas["top_degree"], columns=["Institución", "Centralidad"])
            df_deg["Institución"] = df_deg["Institución"].apply(
                lambda x: x[:55] + "..." if len(x) > 55 else x
            )
            st.dataframe(df_deg, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("#### Betweenness (top 10)")
        if metricas.get("top_betweenness"):
            df_bet = pd.DataFrame(metricas["top_betweenness"], columns=["Institución", "Betweenness"])
            df_bet["Institución"] = df_bet["Institución"].apply(
                lambda x: x[:55] + "..." if len(x) > 55 else x
            )
            st.dataframe(df_bet, use_container_width=True, hide_index=True)

    st.divider()
    with st.expander("Ver tabla completa de nodos"):
        df_nodos = tabla_nodos(G)
        df_nodos["institucion"] = df_nodos["institucion"].apply(
            lambda x: x[:70] + "..." if len(x) > 70 else x
        )
        st.dataframe(df_nodos, use_container_width=True, hide_index=True)
