from pathlib import Path
import html
import pandas as pd
import plotly.express as px
import plotly.io as pio


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "outputs" / "indicadores"
DOCS_DIR = BASE_DIR / "docs"
HTML_PATH = DOCS_DIR / "issue_43" / "indicadores_issue43.html"

(DOCS_DIR / "issue_43").mkdir(parents=True, exist_ok=True)


INDICADORES = [
    {
        "id": "produccion_total",
        "archivo": "01_produccion_total_region_match.csv",
        "titulo": "1. Producción total por región",
        "formula": r"\[P_r = \sum_{i=1}^{n_r} 1\]",
        "descripcion": "Número total de productos científicos registrados en cada región.",
        "interpretacion": "Mide el volumen absoluto de producción científica por región. Sirve como contexto inicial, pero no debe usarse como único criterio de comparación.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "produccion_total",
        "color": None,
    },
    {
        "id": "participacion",
        "archivo": "02_participacion_region_match.csv",
        "titulo": "2. Participación porcentual regional",
        "formula": r"\[\%_r = \left(\frac{P_r}{P_t}\right) \times 100\]",
        "descripcion": "Porcentaje de la producción nacional que aporta cada región.",
        "interpretacion": "Permite comparar regiones usando proporciones y no solamente conteos absolutos.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "participacion_pct",
        "color": None,
    },
    {
        "id": "promedio_grupo",
        "archivo": "03_promedio_por_grupo_match.csv",
        "titulo": "3. Producción promedio por grupo",
        "formula": r"\[Prom_r = \frac{P_r}{G_r}\]",
        "descripcion": "Promedio de productos científicos por grupo de investigación en cada región.",
        "interpretacion": "Mide la intensidad promedio de producción por grupo, evitando depender únicamente del tamaño regional.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "promedio_productos_por_grupo",
        "color": None,
    },
    {
        "id": "clasificacion",
        "archivo": "04_produccion_clasificacion_region_match.csv",
        "titulo": "4. Producción por clasificación del grupo",
        "formula": r"\[P_{r,c} = \text{productos de la región } r \text{ asociados a clasificación } c\]",
        "descripcion": "Distribución de productos según la clasificación del grupo de investigación.",
        "interpretacion": "Permite observar si la producción regional se concentra en grupos A1, A, B, C, reconocidos o sin clasificación.",
        "tipo": "grouped_bar",
        "x": "NME_REGION_GR",
        "y": "produccion_total",
        "color": "NME_CLASIFICACION_GR",
    },
    {
        "id": "diversidad",
        "archivo": "05_diversidad_region_match.csv",
        "titulo": "5. Diversidad de producción científica",
        "formula": r"\[D_r = |T_r|\]",
        "descripcion": "Número de tipologías distintas de productos presentes en cada región.",
        "interpretacion": "Mide variedad de producción científica, no volumen.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "tipologias_distintas",
        "color": None,
    },
    {
        "id": "especializacion",
        "archivo": "06_indice_especializacion_productiva_match.csv",
        "titulo": "6. Índice de especialización productiva",
        "formula": r"\[IE_{r,t} = \frac{(P_{r,t}/P_r)}{(P_t/P_T)}\]",
        "descripcion": "Compara la concentración de una tipología en una región frente a la concentración nacional.",
        "interpretacion": "Si el índice es mayor que 1, la región está relativamente especializada en esa tipología.",
        "tipo": "top_bar",
        "x": "NME_REGION_GR",
        "y": "indice_especializacion",
        "color": "NME_TIPOLOGIA_PD",
    },
    {
        "id": "diversidad_relativa",
        "archivo": "07_diversidad_relativa_region_match.csv",
        "titulo": "7. Diversidad relativa regional",
        "formula": r"\[DR_r = \frac{D_r}{P_r}\]",
        "descripcion": "Relación entre número de tipologías distintas y volumen total de producción regional.",
        "interpretacion": "Permite observar qué tan diversa es la producción en relación con el tamaño productivo de la región.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "diversidad_relativa",
        "color": None,
    },
    {
        "id": "permanencia",
        "archivo": "08_permanencia_grupos_region_match.csv",
        "titulo": "8. Permanencia de grupos por región",
        "formula": r"\[PG_r = \frac{\text{grupos presentes en dos o más convocatorias}}{\text{grupos únicos}_r} \times 100\]",
        "descripcion": "Porcentaje de grupos que aparecen en más de una convocatoria.",
        "interpretacion": "Una tasa alta indica mayor estabilidad de los grupos de investigación en el tiempo.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "porcentaje_grupos_permanentes",
        "color": None,
    },
    {
        "id": "crecimiento",
        "archivo": "09_crecimiento_grupos_region_match.csv",
        "titulo": "9. Crecimiento de grupos por región",
        "formula": r"\[Crecimiento = \frac{G_t - G_{t-1}}{G_{t-1}} \times 100\]",
        "descripcion": "Variación porcentual del número de grupos entre convocatorias.",
        "interpretacion": "Valores positivos indican crecimiento; valores negativos indican disminución.",
        "tipo": "grouped_bar",
        "x": "NME_REGION_GR",
        "y": "crecimiento_pct",
        "color": "ID_CONVOCATORIA",
    },
    {
        "id": "consolidacion",
        "archivo": "10_consolidacion_grupos_region_match.csv",
        "titulo": "10. Consolidación de grupos por región",
        "formula": r"\[CG_r = \frac{\text{grupos permanentes}_r}{\text{grupos únicos}_r}\]",
        "descripcion": "Índice que resume la estabilidad de los grupos regionales.",
        "interpretacion": "Un valor más alto indica mayor consolidación temporal de los grupos.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "indice_consolidacion",
        "color": None,
    },
    {
        "id": "renovacion",
        "archivo": "11_renovacion_grupos_region_match.csv",
        "titulo": "11. Renovación de grupos por región",
        "formula": r"\[RG_{r,t} = \text{grupos cuya primera aparición ocurre en la convocatoria } t\]",
        "descripcion": "Identifica la aparición de grupos nuevos por región y convocatoria.",
        "interpretacion": "Permite analizar entrada o renovación de grupos dentro de la estructura regional.",
        "tipo": "grouped_bar",
        "x": "NME_REGION_GR",
        "y": "grupos_nuevos",
        "color": "ID_CONVOCATORIA",
    },
    {
        "id": "genero",
        "archivo": "12_genero_region_match.csv",
        "titulo": "12. Complementario: distribución de registros por género y región",
        "formula": r"\[PG_{r,g} = \frac{P_{r,g}}{P_r} \times 100\]",
        "descripcion": "Distribución porcentual de registros asociados a género del investigador dentro de cada región.",
        "interpretacion": "Es una caracterización complementaria. No reemplaza el análisis territorial principal por grupos.",
        "tipo": "grouped_bar",
        "x": "NME_REGION_GR",
        "y": "participacion_genero_region_pct",
        "color": "NME_GENERO_PR",
    },
    {
        "id": "evolucion_detalle",
        "archivo": "13_evolucion_grupos_detalle_match.csv",
        "titulo": "13. Evolución detallada de grupos",
        "formula": r"\[G_{r,t} = \text{grupos únicos por región y convocatoria}\]",
        "descripcion": "Presenta grupos y productos por región y convocatoria.",
        "interpretacion": "Permite observar la trayectoria regional de grupos y producción científica.",
        "tipo": "line",
        "x": "ID_CONVOCATORIA",
        "y": "grupos_unicos",
        "color": "NME_REGION_GR",
    },
    {
        "id": "evolucion_region",
        "archivo": "14_evolucion_grupos_region_match.csv",
        "titulo": "14. Evolución de grupos por región",
        "formula": r"\[Variación = G_{\text{última convocatoria}} - G_{\text{primera convocatoria}}\]",
        "descripcion": "Resume el cambio en el número de grupos entre convocatorias.",
        "interpretacion": "Permite comparar qué regiones aumentaron o redujeron su número de grupos.",
        "tipo": "bar",
        "x": "NME_REGION_GR",
        "y": "variacion_pct",
        "color": None,
    },
    {
        "id": "participacion_clasificacion",
        "archivo": "15_participacion_clasificacion_region_match.csv",
        "titulo": "15. Participación por clasificación del grupo",
        "formula": r"\[\%C_{r,c} = \frac{P_{r,c}}{P_r} \times 100\]",
        "descripcion": "Participación de cada clasificación del grupo dentro de la producción regional.",
        "interpretacion": "Permite analizar la composición regional según clasificación de los grupos.",
        "tipo": "grouped_bar",
        "x": "NME_REGION_GR",
        "y": "participacion_clasificacion_region_pct",
        "color": "NME_CLASIFICACION_GR",
    },
    {
        "id": "participacion_clasificacion_convocatoria",
        "archivo": "16_participacion_clasificacion_region_convocatoria_match.csv",
        "titulo": "16. Participación por clasificación, región y convocatoria",
        "formula": r"\[\%C_{r,c,t} = \frac{P_{r,c,t}}{P_{r,t}} \times 100\]",
        "descripcion": "Participación de cada clasificación del grupo por región y convocatoria.",
        "interpretacion": "Permite comparar la estructura regional de clasificación en el tiempo.",
        "tipo": "facet_bar",
        "x": "NME_REGION_GR",
        "y": "participacion_clasificacion_region_convocatoria_pct",
        "color": "NME_CLASIFICACION_GR",
    },
]


def leer_csv(nombre_archivo: str) -> pd.DataFrame:
    path = OUTPUT_DIR / nombre_archivo

    if not path.exists():
        print(f"Advertencia: no existe {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "ID_CONVOCATORIA" in df.columns:
        df["ID_CONVOCATORIA"] = df["ID_CONVOCATORIA"].astype(str).str.strip()
        df["ID_CONVOCATORIA"] = df["ID_CONVOCATORIA"].replace({
            "19": "2017",
            "20": "2019",
            "21": "2021",
            "19.0": "2017",
            "20.0": "2019",
            "21.0": "2021",
        })

    return df


def limpiar_regiones_no_validas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "NME_REGION_GR" not in df.columns:
        return df

    invalidas = {
        "",
        "No disponible",
        "Sin información",
        "Sin informacion",
        "No reporta",
        "nan",
        "None",
    }

    df = df.copy()
    return df[~df["NME_REGION_GR"].astype(str).str.strip().isin(invalidas)]


def tabla_html(df: pd.DataFrame, max_rows: int = 35) -> str:
    if df.empty:
        return "<p class='sin-datos'>No hay registros para mostrar.</p>"

    return df.head(max_rows).to_html(
        index=False,
        border=0,
        classes="tabla-resultados",
        escape=True,
    )


def aplicar_layout(fig, titulo: str, alto: int = 510):
    fig.update_layout(
        title=titulo,
        height=alto,
        margin=dict(l=40, r=30, t=70, b=110),
        paper_bgcolor="white",
        plot_bgcolor="#f9fafb",
        font=dict(color="#1f2937"),
        xaxis=dict(tickangle=-25),
        legend=dict(title=None),
    )
    return fig


def grafica_html(item: dict, df: pd.DataFrame) -> str:
    if df.empty:
        return "<p class='sin-datos'>No hay datos disponibles para graficar.</p>"

    df_plot = limpiar_regiones_no_validas(df)

    if df_plot.empty:
        return "<p class='sin-datos'>No hay regiones válidas para graficar.</p>"

    x = item["x"]
    y = item["y"]
    color = item["color"]
    tipo = item["tipo"]

    if x not in df_plot.columns or y not in df_plot.columns:
        return "<p class='sin-datos'>Las columnas necesarias para graficar no están disponibles.</p>"

    if tipo == "bar":
        df_plot = df_plot.sort_values(y, ascending=False)
        fig = px.bar(
            df_plot,
            x=x,
            y=y,
            text=y,
            labels={x: "Región", y: y.replace("_", " ").title()},
        )
        fig.update_traces(textposition="outside")
        fig = aplicar_layout(fig, item["titulo"])

    elif tipo == "top_bar":
        df_plot = df_plot.sort_values(y, ascending=False).head(15)
        fig = px.bar(
            df_plot,
            x=x,
            y=y,
            color=color if color in df_plot.columns else None,
            text=y,
            labels={x: "Región", y: y.replace("_", " ").title()},
        )
        fig.update_traces(textposition="outside")
        fig = aplicar_layout(fig, item["titulo"], alto=560)

    elif tipo == "grouped_bar":
        if color not in df_plot.columns:
            color = None

        if y in df_plot.columns:
            df_plot = df_plot.dropna(subset=[y])

        fig = px.bar(
            df_plot,
            x=x,
            y=y,
            color=color,
            barmode="group",
            text=y,
            labels={x: "Región", y: y.replace("_", " ").title()},
        )
        fig.update_traces(textposition="outside")
        fig = aplicar_layout(fig, item["titulo"], alto=560)

    elif tipo == "line":
        fig = px.line(
            df_plot.sort_values(x),
            x=x,
            y=y,
            color=color if color in df_plot.columns else None,
            markers=True,
            labels={x: "Convocatoria", y: y.replace("_", " ").title()},
        )
        fig = aplicar_layout(fig, item["titulo"], alto=560)

    elif tipo == "facet_bar":
        facet = "ID_CONVOCATORIA" if "ID_CONVOCATORIA" in df_plot.columns else None
        fig = px.bar(
            df_plot,
            x=x,
            y=y,
            color=color if color in df_plot.columns else None,
            facet_col=facet,
            labels={x: "Región", y: y.replace("_", " ").title()},
        )
        fig = aplicar_layout(fig, item["titulo"], alto=590)

    else:
        return "<p class='sin-datos'>Tipo de gráfica no reconocido.</p>"

    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displayModeBar": True},
    )


def generar_html() -> None:
    dataframes = {item["archivo"]: leer_csv(item["archivo"]) for item in INDICADORES}

    # KPIs base desde producción total
    df_prod = dataframes.get("01_produccion_total_region_match.csv", pd.DataFrame())
    df_prod_valida = limpiar_regiones_no_validas(df_prod)

    total_registros = int(df_prod["produccion_total"].sum()) if "produccion_total" in df_prod.columns else 0
    regiones = int(df_prod_valida["NME_REGION_GR"].nunique()) if "NME_REGION_GR" in df_prod_valida.columns else 0

    df_prom = dataframes.get("03_promedio_por_grupo_match.csv", pd.DataFrame())
    grupos = int(df_prom["grupos_unicos"].sum()) if "grupos_unicos" in df_prom.columns else 0

    df_evol = dataframes.get("13_evolucion_grupos_detalle_match.csv", pd.DataFrame())
    convocatorias = int(df_evol["ID_CONVOCATORIA"].nunique()) if "ID_CONVOCATORIA" in df_evol.columns else 0

    botones = []
    secciones = []

    for i, item in enumerate(INDICADORES):
        df = dataframes.get(item["archivo"], pd.DataFrame())
        df_tabla = limpiar_regiones_no_validas(df)

        botones.append(f"""
            <button class="boton" onclick="mostrarIndicador('{item["id"]}')">
                {html.escape(item["titulo"])}
            </button>
        """)

        display = "grid" if i == 0 else "none"

        secciones.append(f"""
            <section id="{item["id"]}" class="seccion" style="display:{display};">
                <div class="panel info">
                    <h2>{html.escape(item["titulo"])}</h2>

                    <h3>Fórmula</h3>
                    <div class="formula">{item["formula"]}</div>

                    <h3>Descripción</h3>
                    <p>{html.escape(item["descripcion"])}</p>

                    <h3>Interpretación técnica</h3>
                    <div class="interpretacion">{html.escape(item["interpretacion"])}</div>

                    <h3>Archivo generado</h3>
                    <p><code>outputs/indicadores/{html.escape(item["archivo"])}</code></p>
                </div>

                <div class="panel resultados">
                    <h3>Gráfica interactiva</h3>
                    <div class="grafica">
                        {grafica_html(item, df)}
                    </div>

                    <h3>Tabla de resultados</h3>
                    <div class="tabla-contenedor">
                        {tabla_html(df_tabla)}
                    </div>
                </div>
            </section>
        """)

    contenido = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Issue #43 - Indicadores regionales</title>

    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <style>
        body {{
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f5f7fb;
            color: #1f2937;
        }}

        header {{
            background: #111827;
            color: white;
            padding: 30px 44px;
        }}

        header h1 {{
            margin: 0;
            font-size: 30px;
        }}

        header p {{
            color: #d1d5db;
            margin-bottom: 0;
        }}

        .contenedor {{
            padding: 24px 36px 42px;
        }}

        .nota-metodologica {{
            background: #fff7ed;
            border-left: 5px solid #f97316;
            border-radius: 10px;
            color: #7c2d12;
            line-height: 1.5;
            margin-bottom: 22px;
            padding: 14px 16px;
        }}

        .resumen {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi {{
            background: white;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}

        .kpi .valor {{
            font-size: 28px;
            font-weight: bold;
            color: #111827;
        }}

        .kpi .etiqueta {{
            font-size: 13px;
            color: #6b7280;
            margin-top: 5px;
        }}

        .botones {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 24px;
        }}

        .boton {{
            border: none;
            border-radius: 10px;
            padding: 12px 14px;
            background: white;
            color: #111827;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            cursor: pointer;
            font-size: 14px;
        }}

        .boton:hover {{
            background: #e5e7eb;
        }}

        .boton.activo {{
            background: #111827;
            color: white;
        }}

        .seccion {{
            grid-template-columns: 0.85fr 1.5fr;
            gap: 24px;
            align-items: start;
        }}

        .panel {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}

        .panel h2 {{
            margin-top: 0;
            color: #111827;
        }}

        .formula {{
            background: #f3f4f6;
            border-radius: 12px;
            padding: 12px;
            overflow-x: auto;
        }}

        .interpretacion {{
            background: #ecfdf5;
            border-left: 5px solid #10b981;
            padding: 14px;
            border-radius: 8px;
            line-height: 1.5;
        }}

        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 5px;
        }}

        .tabla-contenedor {{
            max-height: 430px;
            overflow: auto;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
        }}

        .tabla-resultados {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        .tabla-resultados th {{
            background: #111827;
            color: white;
            position: sticky;
            top: 0;
            z-index: 1;
        }}

        .tabla-resultados th,
        .tabla-resultados td {{
            border-bottom: 1px solid #e5e7eb;
            padding: 9px 10px;
            text-align: left;
        }}

        .tabla-resultados tr:nth-child(even) {{
            background: #f9fafb;
        }}

        .sin-datos {{
            color: #6b7280;
            background: #f9fafb;
            border-radius: 10px;
            padding: 14px;
        }}

        @media (max-width: 1000px) {{
            .seccion {{
                grid-template-columns: 1fr;
            }}

            .resumen {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 650px) {{
            .resumen {{
                grid-template-columns: 1fr;
            }}

            .contenedor {{
                padding: 18px;
            }}
        }}
    </style>
</head>

<body>
    <header>
        <h1>Issue #43 - Indicadores regionales de producción científica</h1>
        <p>Documento técnico de indicadores calculados para el proyecto. Convocatorias 2017, 2019 y 2021.</p>
    </header>

    <div class="contenedor">
        <div class="nota-metodologica">
            <strong>Nota metodológica.</strong>
            El análisis territorial principal se realiza con la variable
            <code>NME_REGION_GR</code>, correspondiente a la región del grupo de investigación.
            Para las visualizaciones principales se excluyen registros con región vacía,
            "No disponible", "Sin información" o "No reporta", porque no corresponden a una
            región territorial interpretable. Los archivos CSV completos permanecen en
            <code>outputs/indicadores</code> para trazabilidad.
        </div>

        <div class="resumen">
            <div class="kpi">
                <div class="valor">{total_registros:,}</div>
                <div class="etiqueta">Productos científicos</div>
            </div>
            <div class="kpi">
                <div class="valor">{regiones:,}</div>
                <div class="etiqueta">Regiones analizadas</div>
            </div>
            <div class="kpi">
                <div class="valor">{grupos:,}</div>
                <div class="etiqueta">Grupos únicos</div>
            </div>
            <div class="kpi">
                <div class="valor">{convocatorias:,}</div>
                <div class="etiqueta">Convocatorias</div>
            </div>
        </div>

        <div class="botones">
            {''.join(botones)}
        </div>

        {''.join(secciones)}
    </div>

    <script>
        function mostrarIndicador(id) {{
            const secciones = document.querySelectorAll(".seccion");
            secciones.forEach(sec => {{
                sec.style.display = "none";
            }});

            const botones = document.querySelectorAll(".boton");
            botones.forEach(btn => {{
                btn.classList.remove("activo");
            }});

            const seleccion = document.getElementById(id);
            if (seleccion) {{
                seleccion.style.display = "grid";
            }}

            const botonActivo = Array.from(botones).find(btn =>
                btn.getAttribute("onclick").includes(id)
            );

            if (botonActivo) {{
                botonActivo.classList.add("activo");
            }}

            setTimeout(() => {{
                window.dispatchEvent(new Event("resize"));
            }}, 200);
        }}

        document.addEventListener("DOMContentLoaded", () => {{
            const primerBoton = document.querySelector(".boton");
            if (primerBoton) {{
                primerBoton.classList.add("activo");
            }}
        }});
    </script>
</body>
</html>
"""

    HTML_PATH.write_text(contenido, encoding="utf-8")
    print(f"HTML generado correctamente en: {HTML_PATH}")


if __name__ == "__main__":
    generar_html()
