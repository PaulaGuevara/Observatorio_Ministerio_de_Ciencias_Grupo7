from __future__ import annotations

from pathlib import Path
import unicodedata

import folium
from branca.colormap import LinearColormap
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "datos" / "processed" / "indicadores"

REGIONES_ORDEN = [
    "Caribe",
    "Centro Oriente",
    "Centro Sur",
    "Distrito Capital",
    "Eje Cafetero",
    "Llano",
    "Pacífico",
]

REGION_CENTROIDES = {
    "Caribe": (10.5, -75.0),
    "Centro Oriente": (5.8, -73.1),
    "Centro Sur": (1.9, -75.3),
    "Distrito Capital": (4.65, -74.1),
    "Eje Cafetero": (5.0, -75.7),
    "Llano": (4.3, -72.1),
    "Pacífico": (3.7, -77.1),
}

FILES = {
    "01": "01_produccion_total_region_match.csv",
    "01b": "01b_produccion_total_region_convocatoria_match.csv",
    "02": "02_participacion_region_match.csv",
    "02b": "02b_participacion_region_convocatoria_match.csv",
    "03": "03_promedio_por_grupo_match.csv",
    "03b": "03b_promedio_por_grupo_convocatoria_match.csv",
    "04": "04_produccion_clasificacion_region_match.csv",
    "04b": "04b_produccion_clasificacion_region_convocatoria_match.csv",
    "05": "05_diversidad_region_match.csv",
    "05b": "05b_diversidad_region_convocatoria_match.csv",
    "06": "06_indice_especializacion_productiva_match.csv",
    "07": "07_diversidad_relativa_region_match.csv",
    "08": "08_permanencia_grupos_region_match.csv",
    "09": "09_crecimiento_grupos_region_match.csv",
    "10": "10_consolidacion_grupos_region_match.csv",
    "11": "11_renovacion_grupos_region_match.csv",
    "12": "12_genero_region_match.csv",
    "14": "14_evolucion_grupos_region_match.csv",
    "15": "15_participacion_clasificacion_region_match.csv",
    "16": "16_participacion_clasificacion_region_convocatoria_match.csv",
}

METRICS = {
    "1. Producción total por región": {
        "file_all": "01",
        "file_year": "01b",
        "value_col": "produccion_total",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Producción total",
        "suffix": "",
        "decimals": 0,
        "agg": "sum",
    },
    "2. Participación regional": {
        "file_all": "02",
        "file_year": "02b",
        "value_col": "participacion_porcentual",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Participación (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "3. Producción promedio por grupo": {
        "file_all": "03",
        "file_year": "03b",
        "value_col": "produccion_promedio_por_grupo",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Promedio por grupo",
        "suffix": "",
        "decimals": 2,
        "agg": "mean",
    },
    "4. Producción por clasificación del grupo": {
        "file_all": "04",
        "file_year": "04b",
        "value_col": "productos",
        "group_col": "NME_CLASIFICACION_GR",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Productos",
        "suffix": "",
        "decimals": 0,
        "agg": "sum",
    },
    "5. Diversificación de productos": {
        "file_all": "05",
        "file_year": "05b",
        "value_col": "tipologias_distintas",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Tipologías distintas",
        "suffix": "",
        "decimals": 0,
        "agg": "max",
    },
    "6. Índice de especialización productiva": {
        "file_all": "06",
        "value_col": "indice_especializacion_productiva",
        "region_col": "NME_REGION_GR",
        "label": "Índice",
        "suffix": "",
        "decimals": 3,
        "agg": "mean",
    },
    "7. Diversidad relativa de productos": {
        "file_all": "07",
        "value_col": "diversidad_relativa_porcentual",
        "region_col": "NME_REGION_GR",
        "label": "Diversidad relativa (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "8. Tasa de permanencia de grupos": {
        "file_all": "08",
        "value_col": "tasa_permanencia_grupos",
        "region_col": "NME_REGION_GR",
        "label": "Permanencia (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "9. Crecimiento neto de grupos 2017-2021": {
        "file_all": "09",
        "value_col": "crecimiento_porcentual_grupos",
        "region_col": "NME_REGION_GR",
        "label": "Crecimiento (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "10. Fortaleza A1/A en 2021": {
        "file_all": "10",
        "value_col": "fortaleza_a1_a_2021",
        "region_col": "NME_REGION_GR",
        "label": "Fortaleza A1/A (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "11. Tasa de renovación de grupos": {
        "file_all": "11",
        "value_col": "tasa_renovacion_grupos",
        "region_col": "NME_REGION_GR",
        "label": "Renovación (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "12. Complementario: distribución por género registrado": {
        "file_all": "12",
        "value_col": "participacion_porcentual_genero_region",
        "group_col": "NME_GENERO_PR",
        "region_col": "NME_REGION_GR",
        "label": "Participación género (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
        "map_value_col": "productos",
    },
    "13. Evolución de grupos 2017-2021": {
        "file_all": "14",
        "value_col": "tasa_grupos_crecen",
        "region_col": "NME_REGION_GR",
        "label": "Tasa grupos que crecen (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
        "special": "evolucion",
    },
    "14. Participación porcentual por clasificación del grupo": {
        "file_all": "15",
        "value_col": "participacion_clasificacion_region",
        "group_col": "NME_CLASIFICACION_GR",
        "region_col": "NME_REGION_GR",
        "label": "Participación clasificación (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
    "15. Participación porcentual por clasificación, región y convocatoria": {
        "file_all": "16",
        "value_col": "participacion_clasificacion_region_convocatoria",
        "group_col": "NME_CLASIFICACION_GR",
        "region_col": "NME_REGION_GR",
        "year_col": "ANIO_CONVOCATORIA",
        "label": "Participación clasificación convocatoria (%)",
        "suffix": "%",
        "decimals": 2,
        "agg": "mean",
    },
}

FILTRABLES_ANIO = [name for name, c in METRICS.items() if c.get("file_year") or c.get("year_col")]
ESTRUCTURALES = [name for name, c in METRICS.items() if name not in FILTRABLES_ANIO]
METRICS_VISIBLES = FILTRABLES_ANIO

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

st.set_page_config(page_title="Dashboard USTA", page_icon="📊", layout="wide")


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.upper()


def normalize_region(value: object) -> object:
    mapping = {
        "CARIBE": "Caribe",
        "CENTRO ORIENTE": "Centro Oriente",
        "CENTRO SUR": "Centro Sur",
        "DISTRITO CAPITAL": "Distrito Capital",
        "EJE CAFETERO": "Eje Cafetero",
        "LLANO": "Llano",
        "PACIFICO": "Pacífico",
    }
    return mapping.get(normalize_text(value), value)


def format_value(value: object, suffix: str = "", decimals: int = 1) -> str:
    if pd.isna(value):
        return "s.d."
    n = float(value)
    fmt = f"{{:,.{decimals}f}}" if decimals > 0 else "{:,.0f}"
    text = fmt.format(n).replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text}{suffix}"


def missing_files() -> list[str]:
    return [v for v in FILES.values() if not (INPUT_DIR / v).exists()]


def get_logo_path() -> Path | None:
    candidates = [
        BASE_DIR / "app" / "assets" / "logo_usta.png",
        BASE_DIR / "app" / "assets" / "logo.png",
        BASE_DIR / "app" / "assets" / "logo.jpg",
        BASE_DIR / "dashboard" / "assets" / "logo_usta.png",
        BASE_DIR / "dashboard" / "assets" / "logo.png",
        BASE_DIR / "assets" / "logo_usta.png",
        BASE_DIR / "logo_usta.png",
        BASE_DIR / "logo.png",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


@st.cache_data(show_spinner=False)
def read_csv(file_name: str) -> pd.DataFrame:
    return pd.read_csv(INPUT_DIR / file_name)


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}
    for key, file_name in FILES.items():
        df = read_csv(file_name)
        data[key] = df
        # Alias por nombre de archivo para tolerar cachés/formatos anteriores.
        data[file_name] = df
    return data


def resolve_dataset(all_data: dict[str, pd.DataFrame], key: str) -> pd.DataFrame:
    if key in all_data:
        return all_data[key]

    file_name = FILES.get(key)
    if file_name and file_name in all_data:
        return all_data[file_name]

    raise KeyError(
        f"No se encontró la clave '{key}' en datos cargados. "
        "Recarga la app o limpia caché de Streamlit."
    )


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: #f7fafc; color:#0b2745; }
            .hero { background:#003B7A; color:white; border-radius:12px; padding:1rem 1.2rem; }
            .kpi { background:white; border:1px solid #d6deea; border-radius:10px; padding:.7rem .8rem; min-height:100px; }
            .kpi-title { font-size:.84rem; color:#36587b; font-weight:800; }
            .kpi-value { font-size:1.45rem; color:#002147; font-weight:900; line-height:1.1; margin-top:.16rem; }
            .kpi-sub { font-size:.85rem; color:#4a6685; margin-top:.18rem; }
            .tag-title { font-size:1.02rem; font-weight:800; color:#0d2f57; margin:.35rem 0 .2rem; }
            .logo-box { background:#fffdf8; border:1px solid #d6deea; border-radius:12px; padding:.6rem; text-align:center; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_region(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col not in df.columns:
        return df.copy()
    out = df.copy()
    out[col] = out[col].map(normalize_region)
    return out[out[col].isin(REGIONES_ORDEN)].copy()


def metric_df(all_data: dict[str, pd.DataFrame], metric: str, year: str, region: str) -> tuple[pd.DataFrame, dict, bool]:
    cfg = METRICS[metric]
    year_applied = False

    key = cfg["file_all"]
    if year != "Todas" and cfg.get("file_year"):
        key = cfg["file_year"]

    df = resolve_dataset(all_data, key).copy()
    rcol = cfg["region_col"]
    df = ensure_region(df, rcol)

    ycol = cfg.get("year_col")
    if year != "Todas" and ycol and ycol in df.columns:
        df = df[df[ycol] == int(year)].copy()
        year_applied = True

    if year != "Todas" and not year_applied and cfg.get("file_year"):
        # file_year exists but no explicit ANIO col check needed if already selected by key
        year_applied = True

    if region != "Todas":
        df = df[df[rcol] == region].copy()

    return df, cfg, year_applied


def map_frame(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    if df.empty:
        return df
    rcol = cfg["region_col"]
    vcol = cfg.get("map_value_col", cfg["value_col"])
    agg = cfg.get("agg", "mean")
    return df.groupby(rcol, dropna=False).agg(valor=(vcol, agg)).reset_index()


def folium_map(df: pd.DataFrame, cfg: dict, title: str, region: str):
    vals = df["valor"].replace([np.inf, -np.inf], np.nan).dropna()
    vmin = float(vals.min()) if not vals.empty else 0
    vmax = float(vals.max()) if not vals.empty else 1
    if vmin == vmax:
        vmin = 0

    cmap = LinearColormap(["#dceafe", "#003B7A", "#F2A900"], vmin=vmin, vmax=vmax)
    m = folium.Map(location=[4.6, -74.0], zoom_start=5.3, tiles="CartoDB positron")

    by_region = {r[cfg["region_col"]]: r for _, r in df.iterrows()}
    for reg in REGIONES_ORDEN:
        lat, lon = REGION_CENTROIDES[reg]
        row = by_region.get(reg)
        val = np.nan if row is None else row["valor"]
        color = "#9ca3af" if pd.isna(val) else cmap(float(val))
        folium.CircleMarker(
            location=[lat, lon],
            radius=12 if reg == region else 9,
            color="#002147",
            weight=4 if reg == region else 2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=reg,
            popup=f"{title}: {format_value(val, cfg['suffix'], cfg['decimals'])}",
        ).add_to(m)

    cmap.caption = title
    cmap.add_to(m)
    return m


def main_chart(df: pd.DataFrame, cfg: dict, metric: str):
    if df.empty:
        return px.bar(title="Sin datos para este filtro")

    rcol = cfg["region_col"]
    vcol = cfg["value_col"]
    gcol = cfg.get("group_col")

    if cfg.get("special") == "evolucion":
        use = ["grupos_nuevos", "grupos_desaparecen", "grupos_crecen", "grupos_decrecen", "grupos_estables"]
        long = df.melt(id_vars=[rcol], value_vars=use, var_name="categoria", value_name="grupos")
        return px.bar(long, x=rcol, y="grupos", color="categoria", barmode="group", title=metric)

    if gcol and gcol in df.columns:
        return px.bar(df, x=rcol, y=vcol, color=gcol, barmode="stack", title=metric)

    order_df = df.sort_values(vcol, ascending=False)
    return px.bar(
        order_df,
        x=rcol,
        y=vcol,
        color=vcol,
        title=metric,
        color_continuous_scale=["#dceafe", "#003B7A", "#F2A900"],
    )


def support_chart(all_data: dict[str, pd.DataFrame], cfg: dict, metric: str, region: str):
    key = cfg.get("file_year") or cfg["file_all"]
    df = resolve_dataset(all_data, key).copy()
    rcol = cfg["region_col"]
    df = ensure_region(df, rcol)
    if region != "Todas":
        df = df[df[rcol] == region].copy()

    ycol = cfg.get("year_col")
    vcol = cfg["value_col"]
    if ycol and ycol in df.columns:
        agg = df.groupby([ycol, rcol], dropna=False).agg(valor=(vcol, "mean")).reset_index()
        return px.line(agg, x=ycol, y="valor", color=rcol, markers=True, title=f"Tendencia: {metric}")

    agg = df.groupby(rcol, dropna=False).agg(valor=(vcol, "mean")).reset_index().sort_values("valor")
    return px.bar(agg, x="valor", y=rcol, orientation="h", title=f"Comparación regional: {metric}")


def kpis(df: pd.DataFrame, cfg: dict) -> list[dict[str, str]]:
    if df.empty:
        return [
            {"t": "Registros", "v": "0", "s": "Sin datos"},
            {"t": "Regiones", "v": "0", "s": "Cobertura"},
            {"t": "Promedio", "v": "s.d.", "s": cfg["label"]},
            {"t": "Máximo", "v": "s.d.", "s": "Líder"},
        ]

    rcol = cfg["region_col"]
    mf = map_frame(df, cfg)
    mean_v = float(mf["valor"].mean()) if not mf.empty else np.nan
    top = mf.sort_values("valor", ascending=False).iloc[0] if not mf.empty else None

    return [
        {"t": "Registros", "v": format_value(len(df), "", 0), "s": "Después de filtros"},
        {"t": "Regiones", "v": format_value(df[rcol].nunique(), "", 0), "s": "Cobertura"},
        {"t": "Promedio", "v": format_value(mean_v, cfg["suffix"], cfg["decimals"]), "s": cfg["label"]},
        {
            "t": "Región líder",
            "v": "s.d." if top is None else str(top[rcol]),
            "s": "s.d." if top is None else format_value(top["valor"], cfg["suffix"], cfg["decimals"]),
        },
    ]


def metric_leader_value(all_data: dict[str, pd.DataFrame], metric_name: str, year: str, region: str) -> tuple[str, str]:
    df, cfg, _ = metric_df(all_data, metric_name, year, region)
    if df.empty:
        return "s.d.", "Sin datos"

    mf = map_frame(df, cfg)
    if mf.empty:
        return "s.d.", "Sin datos"

    top = mf.sort_values("valor", ascending=False).iloc[0]
    return str(top[cfg["region_col"]]), format_value(top["valor"], cfg["suffix"], cfg["decimals"])


def summary_cards(all_data: dict[str, pd.DataFrame], year: str, region: str) -> list[dict[str, str]]:
    cards_cfg = [
        "1. Producción total por región",
        "2. Participación regional",
        "3. Producción promedio por grupo",
        "4. Producción por clasificación del grupo",
        "5. Diversificación de productos",
        "15. Participación porcentual por clasificación, región y convocatoria",
    ]

    cards: list[dict[str, str]] = []
    for metric_name in cards_cfg:
        # Requisito de negocio: con filtros Todas/Todas en producción total,
        # mostrar total nacional en lugar de solo región líder.
        if metric_name == "1. Producción total por región" and year == "Todas" and region == "Todas":
            df, cfg, _ = metric_df(all_data, metric_name, year, region)
            mf = map_frame(df, cfg)
            total = float(mf["valor"].sum()) if not mf.empty else np.nan
            cards.append(
                {
                    "metric": metric_name,
                    "title": metric_name.split(". ", 1)[1],
                    "value": format_value(total, cfg["suffix"], cfg["decimals"]),
                    "sub": "Total nacional",
                }
            )
            continue

        reg, val = metric_leader_value(all_data, metric_name, year, region)
        cards.append(
            {
                "metric": metric_name,
                "title": metric_name.split(". ", 1)[1],
                "value": val,
                "sub": f"Región líder: {reg}",
            }
        )
    return cards


def purpose_and_analysis(df: pd.DataFrame, cfg: dict, metric: str, year: str, region: str) -> tuple[str, str]:
    purpose = f"Este indicador ({metric}) se usa para evaluar {cfg['label'].lower()} en el contexto regional."
    if cfg.get("year_col") or cfg.get("file_year"):
        purpose += " Es sensible al filtro de convocatoria cuando existe desagregación anual."
    else:
        purpose += " Es estructural en la base actual, por lo que no cambia con convocatoria."

    if df.empty:
        return purpose, "No hay datos suficientes con el filtro actual para generar análisis."

    mf = map_frame(df, cfg)
    if mf.empty:
        return purpose, "No hay agregados regionales para el filtro actual."

    top = mf.sort_values("valor", ascending=False).iloc[0]
    avg = float(mf["valor"].mean())
    analysis = (
        f"Con filtro Convocatoria={year} y Región={region}, la región líder es {top[cfg['region_col']]} "
        f"con {format_value(top['valor'], cfg['suffix'], cfg['decimals'])}. "
        f"Promedio regional del filtro: {format_value(avg, cfg['suffix'], cfg['decimals'])}."
    )
    return purpose, analysis


def main() -> None:
    apply_theme()

    missing = missing_files()
    if missing:
        st.error("Faltan CSV requeridos: " + ", ".join(missing))
        st.stop()

    all_data = load_data()

    st.markdown(
        """
        <div class='hero'>
            <h2 style='margin:0;'>Dashboard analítico regional de producción científica</h2>
            <p style='margin:.35rem 0 0;'>Métricas alineadas a indicadores_regionales_ampliado y validadas con disponibilidad real de datos.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Panel lateral")
        logo = get_logo_path()
        if logo is not None:
            st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
            st.image(str(logo), width=120)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='logo-box'><b>Logo USTA</b><br><small>Agrega logo_usta.png en dashboard/assets</small></div>",
                unsafe_allow_html=True,
            )
        st.markdown("", unsafe_allow_html=True)

        year = st.selectbox("Convocatoria", ["Todas", "2017", "2019", "2021"], index=0)
        region = st.selectbox("Región", ["Todas"] + REGIONES_ORDEN, index=0)

        default_metric = st.session_state.get("selected_metric", METRICS_VISIBLES[0])
        metric = st.selectbox(
            "Métrica principal",
            METRICS_VISIBLES,
            index=METRICS_VISIBLES.index(default_metric) if default_metric in METRICS_VISIBLES else 0,
        )
        map_metric = metric

    st.session_state["selected_metric"] = metric
    df_metric, cfg_metric, year_ok_metric = metric_df(all_data, metric, year, region)
    df_map_raw, cfg_map, year_ok_map = metric_df(all_data, map_metric, year, region)

    cards = summary_cards(all_data, year, region)
    cols = st.columns(6, gap="small")
    for i, (c, item) in enumerate(zip(cols, cards)):
        with c:
            st.markdown(
                f"""
                <div class='kpi'>
                    <div class='kpi-title'>{item['title']}</div>
                    <div class='kpi-value'>{item['value']}</div>
                    <div class='kpi-sub'>{item['sub']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Ver: {i+1}", key=f"card_{i}"):
                st.session_state["selected_metric"] = item["metric"]
                st.rerun()

    st.markdown("<div class='tag-title'>Métricas disponibles</div>", unsafe_allow_html=True)
    metric = st.radio(
        "metric_tags",
        METRICS_VISIBLES,
        index=METRICS_VISIBLES.index(st.session_state.get("selected_metric", metric))
        if st.session_state.get("selected_metric", metric) in METRICS_VISIBLES
        else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["selected_metric"] = metric
    df_metric, cfg_metric, year_ok_metric = metric_df(all_data, metric, year, region)

    mf = map_frame(df_map_raw, cfg_map)
    if mf.empty:
        st.warning("No hay datos para el mapa con el filtro actual.")
        st.stop()

    col_map, col_rank = st.columns([1.5, 1], gap="small")
    with col_map:
        st.markdown("**Mapa regional interactivo**")
        fmap = folium_map(mf, cfg_map, map_metric, region)
        st_folium(fmap, height=470, use_container_width=True)

    with col_rank:
        rank = mf.sort_values("valor", ascending=False)
        rank_fig = px.bar(
            rank,
            x="valor",
            y=cfg_map["region_col"],
            orientation="h",
            color="valor",
            title=f"Ranking: {map_metric}",
            color_continuous_scale=["#dceafe", "#003B7A", "#F2A900"],
        )
        rank_fig.update_layout(height=470)
        st.plotly_chart(rank_fig, use_container_width=True, config=PLOT_CONFIG)

    left, right = st.columns([1.7, 1], gap="small")
    with left:
        fig1 = main_chart(df_metric, cfg_metric, metric)
        fig1.update_layout(height=430)
        st.plotly_chart(fig1, use_container_width=True, config=PLOT_CONFIG)

        fig2 = support_chart(all_data, cfg_metric, metric, region)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True, config=PLOT_CONFIG)

    with right:
        purpose, analysis = purpose_and_analysis(df_metric, cfg_metric, metric, year, region)
        st.markdown("### ¿Para qué sirve este cálculo?")
        st.markdown(purpose)
        st.markdown("### Análisis del resultado")
        st.markdown(analysis)


if __name__ == "__main__":
    main()
