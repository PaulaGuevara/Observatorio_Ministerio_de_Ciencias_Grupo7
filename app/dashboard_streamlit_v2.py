from __future__ import annotations

import base64
import math

import streamlit as st
import plotly.express as px
from streamlit_folium import st_folium

import dashboard_streamlit_final as base


def _fmt2(value: object) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(n) or math.isinf(n):
        return "s.d."
    return base.format_value(n, "", 2)


def add_visible_values(fig, decimals: int = 2):
    for trace in fig.data:
        if trace.type == "bar":
            if getattr(trace, "orientation", "v") == "h":
                seq = trace.x if trace.x is not None else []
                trace.text = [_fmt2(v) for v in seq]
                trace.texttemplate = "%{text}"
                trace.textposition = "outside"
                trace.cliponaxis = False
            else:
                seq = trace.y if trace.y is not None else []
                trace.text = [_fmt2(v) for v in seq]
                trace.texttemplate = "%{text}"
                trace.textposition = "outside"
                trace.cliponaxis = False
        elif trace.type == "scatter":
            mode = getattr(trace, "mode", "lines+markers")
            if "text" not in mode:
                trace.mode = f"{mode}+text"
            seq = trace.y if trace.y is not None else trace.x
            trace.text = [_fmt2(v) for v in seq] if seq is not None else None
            trace.textposition = "top center"
    return fig


def apply_numeric_axes(fig):
    fig.update_xaxes(tickformat=",.2f", separatethousands=True)
    fig.update_yaxes(tickformat=",.2f", separatethousands=True)
    return fig


def metric_leader_value_v2(all_data: dict, metric_name: str, year: str, region: str) -> tuple[str, str]:
    df, cfg, _ = base.metric_df(all_data, metric_name, year, region)
    if df.empty:
        return "s.d.", "Sin datos"

    mf = base.map_frame(df, cfg)
    if mf.empty:
        return "s.d.", "Sin datos"

    top = mf.sort_values("valor", ascending=False).iloc[0]
    return str(top[cfg["region_col"]]), base.format_value(top["valor"], cfg.get("suffix", ""), 2)


def summary_cards_v2(all_data: dict, year: str, region: str) -> list[dict[str, str]]:
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
        if metric_name == "1. Producción total por región" and year == "Todas" and region == "Todas":
            df, cfg, _ = base.metric_df(all_data, metric_name, year, region)
            mf = base.map_frame(df, cfg)
            total = float(mf["valor"].sum()) if not mf.empty else float("nan")
            cards.append(
                {
                    "metric": metric_name,
                    "title": metric_name.split(". ", 1)[1],
                    "value": base.format_value(total, cfg.get("suffix", ""), 2),
                    "sub": "Total nacional",
                }
            )
            continue

        reg, val = metric_leader_value_v2(all_data, metric_name, year, region)
        cards.append(
            {
                "metric": metric_name,
                "title": metric_name.split(". ", 1)[1],
                "value": val,
                "sub": f"Región líder: {reg}",
            }
        )
    return cards


def get_logo_path_v2():
    candidates = [
        base.BASE_DIR / "app" / "assets" / "logo.jpg",
        base.BASE_DIR / "app" / "assets" / "logo.jpeg",
        base.BASE_DIR / "app" / "assets" / "logo_usta.png",
        base.BASE_DIR / "dashboard" / "assets" / "logo.jpg",
        base.BASE_DIR / "dashboard" / "assets" / "logo.jpeg",
        base.BASE_DIR / "assets" / "logo.jpg",
        base.BASE_DIR / "logo.jpg",
    ]
    for path in candidates:
        if path.exists():
            return path
    return base.get_logo_path()


def render_sidebar_logo(path) -> None:
    raw = path.read_bytes()
    ext = path.suffix.lower()
    mime = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(raw).decode("ascii")
    st.markdown(
        f"""
        <div style='display:flex; justify-content:center; margin:.25rem 0 1rem 0;'>
            <div style='width:100%; max-width:220px; background:linear-gradient(180deg,#ffffff 0%, #f4f8ff 100%); border:1px solid #d9e3f2; border-radius:14px; padding:.7rem .7rem .55rem; box-shadow:0 8px 20px rgba(0,33,71,.10); text-align:center;'>
                <img src='data:{mime};base64,{encoded}' style='width:132px; height:auto; display:block; margin:0 auto; border-radius:10px;' />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_cards_selector(metrics: list[str], selected_metric: str) -> str:
    st.markdown(
        """
        <style>
            div[data-testid='stButton'] > button {
                min-height: 46px;
                border-radius: 10px;
                border: 1px solid #c9d6ea;
                font-weight: 700;
                color: #0d2f57;
                background: #ffffff;
                white-space: normal;
                line-height: 1.2;
                padding: .45rem .55rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    current = st.session_state.get("selected_metric_v2", selected_metric)
    cards_per_row = 4
    for i in range(0, len(metrics), cards_per_row):
        chunk = metrics[i : i + cards_per_row]
        cols = st.columns(cards_per_row, gap="small")
        for j, metric_name in enumerate(chunk):
            with cols[j]:
                short_title = metric_name.split(". ", 1)[1] if ". " in metric_name else metric_name
                label = short_title
                if metric_name == current:
                    label = f"Seleccionada: {short_title}"

                if st.button(label, key=f"metric_card_v2_{i+j}", use_container_width=True):
                    st.session_state["selected_metric_v2"] = metric_name
                    st.rerun()

    return st.session_state.get("selected_metric_v2", selected_metric)


# Ficha tecnica tomada de docs/indicadores_regionales_ampliado.html
TECH_SHEETS = {
    "1. Producción total por región": {
        "formula": r"P_r = \\sum_{i=1}^{n_r} 1",
        "descripcion": "Número total de productos científicos registrados en cada región.",
        "interpretacion": "Mide volumen absoluto de producción. Sirve como contexto inicial, pero no debe usarse como único criterio de comparación.",
    },
    "2. Participación regional": {
        "formula": r"\\%_r = \\left(\\frac{P_r}{P_t}\\right) \\times 100",
        "descripcion": "Porcentaje de la producción nacional que aporta cada región.",
        "interpretacion": "Permite comparar regiones usando proporciones y no solo conteos absolutos.",
    },
    "3. Producción promedio por grupo": {
        "formula": r"Prom_r = \\frac{P_r}{G_r}",
        "descripcion": "Promedio de productos por grupo de investigación en cada región.",
        "interpretacion": "Mide intensidad promedio de producción por grupo.",
    },
    "4. Producción por clasificación del grupo": {
        "formula": r"P_{r,c} = \\text{productos de la región } r \\text{ asociados a clasificación } c",
        "descripcion": "Distribuye los productos según la clasificación del grupo de investigación.",
        "interpretacion": "Permite observar si la producción regional se concentra en grupos A1/A, B, C o Reconocidos.",
    },
    "5. Diversificación de productos": {
        "formula": r"D_r = |T_r|",
        "descripcion": "Número de tipologías distintas de productos presentes en cada región.",
        "interpretacion": "Mide variedad de producción científica, no volumen.",
    },
    "6. Índice de especialización productiva": {
        "formula": r"IEP_r = \\frac{\\text{participación de productos}_r}{\\text{participación de grupos}_r}",
        "descripcion": "Compara el peso de la región en productos frente a su peso en número de grupos.",
        "interpretacion": "Si el índice es mayor que 1, la región produce proporcionalmente más de lo que representa en grupos.",
    },
    "7. Diversidad relativa de productos": {
        "formula": r"DR_r = \\frac{\\text{tipologías distintas}_r}{\\text{total de tipologías nacionales}} \\times 100",
        "descripcion": "Mide qué proporción de las tipologías nacionales aparece en cada región.",
        "interpretacion": "Convierte la diversidad en un indicador relativo y comparable.",
    },
    "8. Tasa de permanencia de grupos": {
        "formula": r"TP_r = \\frac{\\text{grupos presentes en 2017, 2019 y 2021}}{\\text{total de grupos únicos}_r} \\times 100",
        "descripcion": "Porcentaje de grupos que se mantienen en las tres convocatorias.",
        "interpretacion": "Una tasa alta indica mayor estabilidad de los grupos en el tiempo.",
    },
    "9. Crecimiento neto de grupos 2017-2021": {
        "formula": r"C_r = \\frac{G_{2021} - G_{2017}}{G_{2017}} \\times 100",
        "descripcion": "Mide el crecimiento o decrecimiento relativo de grupos entre 2017 y 2021.",
        "interpretacion": "Valores positivos indican crecimiento; valores negativos indican disminución.",
    },
    "10. Fortaleza A1/A en 2021": {
        "formula": r"FA_{r,2021} = \\frac{\\text{grupos A1 o A en 2021}_r}{\\text{total de grupos clasificados en 2021}_r} \\times 100",
        "descripcion": "Proporción de grupos regionales clasificados como A1 o A en la convocatoria 2021.",
        "interpretacion": "Describe la fortaleza A1/A en 2021. No mide trayectoria histórica; debe leerse junto con permanencia y evolución.",
    },
    "11. Tasa de renovación de grupos": {
        "formula": r"TR_r = \\frac{\\text{grupos en 2021 que no estaban en 2017}}{\\text{grupos de 2021}} \\times 100",
        "descripcion": "Mide la aparición de grupos nuevos en 2021 frente a 2017.",
        "interpretacion": "Una tasa alta puede indicar renovación o expansión de la base de grupos.",
    },
    "12. Complementario: distribución por género registrado": {
        "formula": r"PG_{r,g} = \\frac{P_{r,g}}{P_r} \\times 100",
        "descripcion": "Distribución porcentual de la producción regional según género registrado del investigador.",
        "interpretacion": "Es una caracterización complementaria. No reemplaza el análisis territorial principal por grupos.",
    },
    "13. Evolución de grupos 2017-2021": {
        "formula": r"E_{r} = \\{\\text{nuevos, desaparecen, crecen, decrecen, estables}\\}_{2017-2021}",
        "descripcion": "Clasifica los grupos según su cambio de producción entre 2017 y 2021 y resume el resultado por región.",
        "interpretacion": "Distingue crecimiento, decrecimiento, estabilidad, entrada y salida de grupos.",
    },
    "14. Participación porcentual por clasificación del grupo": {
        "formula": r"\\%_{r,c} = \\frac{P_{r,c}}{P_r} \\times 100",
        "descripcion": "Calcula la participación de cada clasificación de grupo dentro de la producción total de su región.",
        "interpretacion": "Permite comparar composición interna regional por clasificación, no solo volúmenes absolutos.",
    },
    "15. Participación porcentual por clasificación, región y convocatoria": {
        "formula": r"\\%_{r,c,t} = \\frac{P_{r,c,t}}{P_{r,t}} \\times 100",
        "descripcion": "Desagrega la participación por clasificación del grupo para 2017, 2019 y 2021.",
        "interpretacion": "Sirve para leer cambios de composición por clasificación entre convocatorias sin perder el contexto regional.",
    },
}


def tech_panel(metric: str) -> None:
    sheet = TECH_SHEETS.get(metric)
    if not sheet:
        st.info("No hay ficha técnica disponible para este indicador.")
        return

    st.markdown("### Ficha técnica")
    st.markdown("**Fórmula**")
    st.latex(sheet["formula"])
    st.markdown("**Descripción**")
    st.markdown(sheet["descripcion"])
    st.markdown("**Interpretación técnica**")
    st.markdown(sheet["interpretacion"])


def main() -> None:
    base.apply_theme()

    missing = base.missing_files()
    if missing:
        st.error("Faltan CSV requeridos: " + ", ".join(missing))
        st.stop()

    all_data = base.load_data()
    metrics_visibles = list(base.METRICS.keys())

    st.markdown(
        """
        <div class='hero'>
            <h2 style='margin:0;'>Analítica de Investigación Científica en Colombia</h2>
            <p style='margin:.35rem 0 0;'>Integración y análisis de métricas de productos, grupos e investigadores de Minciencias</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Panel lateral")
        logo = get_logo_path_v2()
        if logo is not None:
            render_sidebar_logo(logo)

        year = st.selectbox("Convocatoria", ["Todas", "2017", "2019", "2021"], index=0)
        region = st.selectbox("Región", ["Todas"] + base.REGIONES_ORDEN, index=0)

        default_metric = st.session_state.get("selected_metric_v2", metrics_visibles[0])
        metric = st.selectbox(
            "Métrica principal",
            metrics_visibles,
            index=metrics_visibles.index(default_metric) if default_metric in metrics_visibles else 0,
        )

    st.session_state["selected_metric_v2"] = metric

    df_metric, cfg_metric, _ = base.metric_df(all_data, metric, year, region)
    df_map_raw, cfg_map, _ = base.metric_df(all_data, metric, year, region)

    cards = summary_cards_v2(all_data, year, region)
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
            if st.button(f"Ver: {i+1}", key=f"card_v2_{i}"):
                st.session_state["selected_metric_v2"] = item["metric"]
                st.rerun()

    st.markdown("<div class='tag-title'>Métricas disponibles</div>", unsafe_allow_html=True)
    metric = metric_cards_selector(metrics_visibles, metric)
    st.session_state["selected_metric_v2"] = metric
    df_metric, cfg_metric, _ = base.metric_df(all_data, metric, year, region)
    df_map_raw, cfg_map, _ = base.metric_df(all_data, metric, year, region)
    cfg_metric = dict(cfg_metric)
    cfg_map = dict(cfg_map)
    cfg_metric["decimals"] = 2
    cfg_map["decimals"] = 2

    mf = base.map_frame(df_map_raw, cfg_map)
    if mf.empty:
        st.warning("No hay datos para el mapa con el filtro actual.")
        st.stop()

    col_map, col_rank = st.columns([1.5, 1], gap="small")
    with col_map:
        st.markdown("**Mapa regional interactivo**")
        fmap = base.folium_map(mf, cfg_map, metric, region)
        st_folium(fmap, height=470, use_container_width=True)
        st.markdown("**Resultados del mapa**")
        map_results = mf.sort_values("valor", ascending=False).copy()
        map_results["resultado"] = map_results["valor"].apply(
            lambda v: base.format_value(v, cfg_map["suffix"], cfg_map["decimals"])
        )
        st.dataframe(
            map_results[[cfg_map["region_col"], "resultado"]],
            use_container_width=True,
            height=220,
        )

    with col_rank:
        rank = mf.sort_values("valor", ascending=False)
        rank_fig = px.bar(
            rank,
            x="valor",
            y=cfg_map["region_col"],
            orientation="h",
            color="valor",
            title=f"Ranking: {metric}",
            color_continuous_scale=["#dceafe", "#003B7A", "#F2A900"],
        )
        rank_fig = add_visible_values(rank_fig)
        rank_fig = apply_numeric_axes(rank_fig)
        rank_fig.update_layout(height=470, margin=dict(l=120, r=30, t=60, b=50), uniformtext_minsize=9)
        rank_fig.update_yaxes(automargin=True)
        st.plotly_chart(rank_fig, use_container_width=True, config=base.PLOT_CONFIG)

    left, right = st.columns([1.7, 1], gap="small")
    with left:
        fig1 = base.main_chart(df_metric, cfg_metric, metric)
        fig1 = add_visible_values(fig1)
        fig1 = apply_numeric_axes(fig1)
        fig1.update_layout(height=430)
        st.plotly_chart(fig1, use_container_width=True, config=base.PLOT_CONFIG)

        fig2 = base.support_chart(all_data, cfg_metric, metric, region)
        fig2 = add_visible_values(fig2)
        fig2 = apply_numeric_axes(fig2)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True, config=base.PLOT_CONFIG)

    with right:
        tech_panel(metric)
        st.markdown("### Análisis dinámico")
        _, analysis = base.purpose_and_analysis(df_metric, cfg_metric, metric, year, region)
        st.markdown(analysis)


if __name__ == "__main__":
    main()
