from pathlib import Path
import pandas as pd
import numpy as np
import html


# ============================================================
# ISSUE #43
# Cálculo de indicadores regionales de producción científica
# Fuente: base consolidada en formato Parquet
# ============================================================


BASE_DIR = Path(__file__).resolve().parents[1]

# Se deja compatibilidad por si el repositorio usa "datos" o "data"
PARQUET_CANDIDATES = [
    BASE_DIR / "datos" / "processed" / "consolidado_produccion_investigadores_match.parquet",
    BASE_DIR / "data" / "processed" / "consolidado_produccion_investigadores_match.parquet",
]

OUTPUT_DIR = BASE_DIR / "outputs" / "indicadores"
DOCS_DIR = BASE_DIR / "docs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def find_parquet_path() -> Path:
    """
    Busca el archivo Parquet consolidado en las rutas esperadas del repositorio.
    """
    for path in PARQUET_CANDIDATES:
        if path.exists():
            return path

    rutas = "\n".join(str(p) for p in PARQUET_CANDIDATES)
    raise FileNotFoundError(
        "No se encontró el archivo Parquet consolidado. "
        f"Rutas revisadas:\n{rutas}"
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas eliminando espacios innecesarios.
    No cambia la lógica del proyecto, solo evita errores por espacios accidentales.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Verifica que existan las columnas mínimas requeridas.
    Si falta alguna, detiene el proceso con un mensaje claro.
    """
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(
            "Faltan columnas requeridas para calcular los indicadores: "
            + ", ".join(missing)
        )


def clean_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara variables clave para los cálculos.
    La región principal del análisis es la región del grupo de investigación.
    """
    df = df.copy()

    required = [
        "NME_REGION_GR",
        "COD_GRUPO_GR",
        "ID_CONVOCATORIA",
        "NME_TIPOLOGIA_PD",
        "NME_CLASIFICACION_GR",
    ]
    require_columns(df, required)

    df["NME_REGION_GR"] = df["NME_REGION_GR"].fillna("Sin información").astype(str).str.strip()
    df["COD_GRUPO_GR"] = df["COD_GRUPO_GR"].fillna("Sin código").astype(str).str.strip()
    df["ID_CONVOCATORIA"] = df["ID_CONVOCATORIA"].astype(str).str.strip()
    df["NME_TIPOLOGIA_PD"] = df["NME_TIPOLOGIA_PD"].fillna("Sin tipología").astype(str).str.strip()
    df["NME_CLASIFICACION_GR"] = df["NME_CLASIFICACION_GR"].fillna("Sin clasificación").astype(str).str.strip()

    if "NME_GENERO_PR" in df.columns:
        df["NME_GENERO_PR"] = df["NME_GENERO_PR"].fillna("Sin información").astype(str).str.strip()

    return df


def save_csv(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Guarda cada indicador en outputs/indicadores.
    """
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Archivo generado: {path}")
    return df


def calcular_indicadores(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Calcula los 16 indicadores regionales considerados para el proyecto.
    """
    indicadores = {}

    # ------------------------------------------------------------
    # 1. Producción total por región
    # Fórmula: P_r = sum(1)
    # ------------------------------------------------------------
    prod_region = (
        df.groupby("NME_REGION_GR")
        .size()
        .reset_index(name="produccion_total")
        .sort_values("produccion_total", ascending=False)
    )
    indicadores["01_produccion_total_region_match.csv"] = save_csv(
        prod_region,
        "01_produccion_total_region_match.csv"
    )

    # ------------------------------------------------------------
    # 2. Participación porcentual regional
    # Fórmula: %_r = (P_r / P_t) * 100
    # ------------------------------------------------------------
    total_nacional = prod_region["produccion_total"].sum()
    participacion_region = prod_region.copy()
    participacion_region["participacion_pct"] = (
        participacion_region["produccion_total"] / total_nacional * 100
    ).round(4)
    indicadores["02_participacion_region_match.csv"] = save_csv(
        participacion_region,
        "02_participacion_region_match.csv"
    )

    # ------------------------------------------------------------
    # 3. Producción promedio por grupo
    # Fórmula: Prom_r = P_r / G_r
    # ------------------------------------------------------------
    grupos_region = (
        df.groupby("NME_REGION_GR")["COD_GRUPO_GR"]
        .nunique()
        .reset_index(name="grupos_unicos")
    )

    promedio_grupo = prod_region.merge(grupos_region, on="NME_REGION_GR", how="left")
    promedio_grupo["promedio_productos_por_grupo"] = (
        promedio_grupo["produccion_total"] / promedio_grupo["grupos_unicos"]
    ).round(4)

    indicadores["03_promedio_por_grupo_match.csv"] = save_csv(
        promedio_grupo,
        "03_promedio_por_grupo_match.csv"
    )

    # ------------------------------------------------------------
    # 4. Producción por clasificación del grupo
    # Fórmula: P_{r,c} = número de productos de la región r
    # asociados a grupos de clasificación c
    # ------------------------------------------------------------
    prod_clasificacion = (
        df.groupby(["NME_REGION_GR", "NME_CLASIFICACION_GR"])
        .size()
        .reset_index(name="produccion_total")
        .sort_values(["NME_REGION_GR", "produccion_total"], ascending=[True, False])
    )

    indicadores["04_produccion_clasificacion_region_match.csv"] = save_csv(
        prod_clasificacion,
        "04_produccion_clasificacion_region_match.csv"
    )

    # ------------------------------------------------------------
    # 5. Diversidad de producción científica
    # Fórmula: D_r = |T_r|
    # ------------------------------------------------------------
    diversidad_region = (
        df.groupby("NME_REGION_GR")["NME_TIPOLOGIA_PD"]
        .nunique()
        .reset_index(name="tipologias_distintas")
        .sort_values("tipologias_distintas", ascending=False)
    )

    indicadores["05_diversidad_region_match.csv"] = save_csv(
        diversidad_region,
        "05_diversidad_region_match.csv"
    )

    # ------------------------------------------------------------
    # 6. Índice de especialización productiva
    # Fórmula:
    # IE_{r,t} = (P_{r,t} / P_r) / (P_t / P_T)
    # ------------------------------------------------------------
    region_tipologia = (
        df.groupby(["NME_REGION_GR", "NME_TIPOLOGIA_PD"])
        .size()
        .reset_index(name="produccion_region_tipologia")
    )

    prod_tipologia_nacional = (
        df.groupby("NME_TIPOLOGIA_PD")
        .size()
        .reset_index(name="produccion_tipologia_nacional")
    )

    especializacion = (
        region_tipologia
        .merge(prod_region, on="NME_REGION_GR", how="left")
        .merge(prod_tipologia_nacional, on="NME_TIPOLOGIA_PD", how="left")
    )

    especializacion["participacion_tipologia_region"] = (
        especializacion["produccion_region_tipologia"] / especializacion["produccion_total"]
    )

    especializacion["participacion_tipologia_nacional"] = (
        especializacion["produccion_tipologia_nacional"] / total_nacional
    )

    especializacion["indice_especializacion"] = (
        especializacion["participacion_tipologia_region"]
        / especializacion["participacion_tipologia_nacional"]
    ).round(4)

    especializacion = especializacion.sort_values(
        ["NME_REGION_GR", "indice_especializacion"],
        ascending=[True, False]
    )

    indicadores["06_indice_especializacion_productiva_match.csv"] = save_csv(
        especializacion,
        "06_indice_especializacion_productiva_match.csv"
    )

    # ------------------------------------------------------------
    # 7. Diversidad relativa regional
    # Fórmula: DR_r = D_r / P_r
    # ------------------------------------------------------------
    diversidad_relativa = diversidad_region.merge(prod_region, on="NME_REGION_GR", how="left")
    diversidad_relativa["diversidad_relativa"] = (
        diversidad_relativa["tipologias_distintas"]
        / diversidad_relativa["produccion_total"]
    ).round(6)

    indicadores["07_diversidad_relativa_region_match.csv"] = save_csv(
        diversidad_relativa,
        "07_diversidad_relativa_region_match.csv"
    )

    # ------------------------------------------------------------
    # Base auxiliar de grupos por región y convocatoria
    # ------------------------------------------------------------
    grupo_region_conv = (
        df[["NME_REGION_GR", "COD_GRUPO_GR", "ID_CONVOCATORIA"]]
        .drop_duplicates()
    )

    grupo_region = (
        grupo_region_conv
        .groupby(["NME_REGION_GR", "COD_GRUPO_GR"])["ID_CONVOCATORIA"]
        .nunique()
        .reset_index(name="convocatorias_presentes")
    )

    grupo_region["grupo_permanente"] = grupo_region["convocatorias_presentes"] >= 2

    # ------------------------------------------------------------
    # 8. Permanencia de grupos por región
    # Fórmula: grupos con presencia en dos o más convocatorias
    # ------------------------------------------------------------
    permanencia = (
        grupo_region.groupby("NME_REGION_GR")
        .agg(
            grupos_unicos=("COD_GRUPO_GR", "nunique"),
            grupos_permanentes=("grupo_permanente", "sum"),
            promedio_convocatorias_por_grupo=("convocatorias_presentes", "mean")
        )
        .reset_index()
    )

    permanencia["porcentaje_grupos_permanentes"] = (
        permanencia["grupos_permanentes"] / permanencia["grupos_unicos"] * 100
    ).round(4)

    permanencia["promedio_convocatorias_por_grupo"] = (
        permanencia["promedio_convocatorias_por_grupo"].round(4)
    )

    indicadores["08_permanencia_grupos_region_match.csv"] = save_csv(
        permanencia,
        "08_permanencia_grupos_region_match.csv"
    )

    # ------------------------------------------------------------
    # 9. Crecimiento de grupos por región
    # Fórmula: crecimiento = ((G_t - G_{t-1}) / G_{t-1}) * 100
    # ------------------------------------------------------------
    grupos_conv = (
        grupo_region_conv.groupby(["NME_REGION_GR", "ID_CONVOCATORIA"])["COD_GRUPO_GR"]
        .nunique()
        .reset_index(name="grupos_unicos")
        .sort_values(["NME_REGION_GR", "ID_CONVOCATORIA"])
    )

    grupos_conv["grupos_periodo_anterior"] = (
        grupos_conv.groupby("NME_REGION_GR")["grupos_unicos"].shift(1)
    )

    grupos_conv["crecimiento_pct"] = (
        (grupos_conv["grupos_unicos"] - grupos_conv["grupos_periodo_anterior"])
        / grupos_conv["grupos_periodo_anterior"]
        * 100
    ).round(4)

    indicadores["09_crecimiento_grupos_region_match.csv"] = save_csv(
        grupos_conv,
        "09_crecimiento_grupos_region_match.csv"
    )

    # ------------------------------------------------------------
    # 10. Consolidación de grupos por región
    # Fórmula: CG_r = grupos permanentes / grupos únicos
    # ------------------------------------------------------------
    consolidacion = permanencia.copy()
    consolidacion["indice_consolidacion"] = (
        consolidacion["grupos_permanentes"] / consolidacion["grupos_unicos"]
    ).round(4)

    indicadores["10_consolidacion_grupos_region_match.csv"] = save_csv(
        consolidacion,
        "10_consolidacion_grupos_region_match.csv"
    )

    # ------------------------------------------------------------
    # 11. Renovación de grupos por región
    # Fórmula: grupos nuevos en cada convocatoria
    # ------------------------------------------------------------
    first_conv = (
        grupo_region_conv
        .groupby(["NME_REGION_GR", "COD_GRUPO_GR"])["ID_CONVOCATORIA"]
        .min()
        .reset_index(name="primera_convocatoria")
    )

    renovacion = (
        first_conv.groupby(["NME_REGION_GR", "primera_convocatoria"])["COD_GRUPO_GR"]
        .nunique()
        .reset_index(name="grupos_nuevos")
        .rename(columns={"primera_convocatoria": "ID_CONVOCATORIA"})
        .sort_values(["NME_REGION_GR", "ID_CONVOCATORIA"])
    )

    indicadores["11_renovacion_grupos_region_match.csv"] = save_csv(
        renovacion,
        "11_renovacion_grupos_region_match.csv"
    )

    # ------------------------------------------------------------
    # 12. Distribución por género y región
    # Fórmula: conteo y participación por género dentro de cada región
    # ------------------------------------------------------------
    if "NME_GENERO_PR" in df.columns:
        genero_region = (
            df.groupby(["NME_REGION_GR", "NME_GENERO_PR"])
            .size()
            .reset_index(name="registros")
        )

        total_genero_region = (
            genero_region.groupby("NME_REGION_GR")["registros"]
            .sum()
            .reset_index(name="total_region")
        )

        genero_region = genero_region.merge(total_genero_region, on="NME_REGION_GR", how="left")
        genero_region["participacion_genero_region_pct"] = (
            genero_region["registros"] / genero_region["total_region"] * 100
        ).round(4)
    else:
        genero_region = pd.DataFrame({
            "mensaje": ["No se encontró la columna NME_GENERO_PR en la base consolidada."]
        })

    indicadores["12_genero_region_match.csv"] = save_csv(
        genero_region,
        "12_genero_region_match.csv"
    )

    # ------------------------------------------------------------
    # 13. Evolución detallada de grupos
    # Fórmula: grupos y productos por región y convocatoria
    # ------------------------------------------------------------
    productos_conv = (
        df.groupby(["NME_REGION_GR", "ID_CONVOCATORIA"])
        .size()
        .reset_index(name="produccion_total")
    )

    evolucion_detalle = grupos_conv.merge(
        productos_conv,
        on=["NME_REGION_GR", "ID_CONVOCATORIA"],
        how="left"
    )

    indicadores["13_evolucion_grupos_detalle_match.csv"] = save_csv(
        evolucion_detalle,
        "13_evolucion_grupos_detalle_match.csv"
    )

    # ------------------------------------------------------------
    # 14. Evolución de grupos por región
    # Fórmula: comparación de grupos únicos entre convocatorias
    # ------------------------------------------------------------
    evolucion_wide = grupos_conv.pivot_table(
        index="NME_REGION_GR",
        columns="ID_CONVOCATORIA",
        values="grupos_unicos",
        fill_value=0
    ).reset_index()

    evolucion_wide.columns = [str(c) for c in evolucion_wide.columns]

    convocatorias = sorted([c for c in evolucion_wide.columns if c != "NME_REGION_GR"])
    if len(convocatorias) >= 2:
        primera = convocatorias[0]
        ultima = convocatorias[-1]
        evolucion_wide["variacion_absoluta"] = evolucion_wide[ultima] - evolucion_wide[primera]
        evolucion_wide["variacion_pct"] = np.where(
            evolucion_wide[primera] > 0,
            (evolucion_wide["variacion_absoluta"] / evolucion_wide[primera] * 100).round(4),
            np.nan
        )

    indicadores["14_evolucion_grupos_region_match.csv"] = save_csv(
        evolucion_wide,
        "14_evolucion_grupos_region_match.csv"
    )

    # ------------------------------------------------------------
    # 15. Participación por clasificación del grupo
    # Fórmula: participación de cada clasificación dentro de la región
    # ------------------------------------------------------------
    total_region_clasif = (
        prod_clasificacion.groupby("NME_REGION_GR")["produccion_total"]
        .sum()
        .reset_index(name="total_region")
    )

    participacion_clasificacion = prod_clasificacion.merge(
        total_region_clasif,
        on="NME_REGION_GR",
        how="left"
    )

    participacion_clasificacion["participacion_clasificacion_region_pct"] = (
        participacion_clasificacion["produccion_total"]
        / participacion_clasificacion["total_region"]
        * 100
    ).round(4)

    indicadores["15_participacion_clasificacion_region_match.csv"] = save_csv(
        participacion_clasificacion,
        "15_participacion_clasificacion_region_match.csv"
    )

    # ------------------------------------------------------------
    # 16. Participación por clasificación, región y convocatoria
    # Fórmula: participación de clasificación dentro de región y convocatoria
    # ------------------------------------------------------------
    clasif_region_conv = (
        df.groupby(["NME_REGION_GR", "ID_CONVOCATORIA", "NME_CLASIFICACION_GR"])
        .size()
        .reset_index(name="produccion_total")
    )

    total_region_conv = (
        clasif_region_conv.groupby(["NME_REGION_GR", "ID_CONVOCATORIA"])["produccion_total"]
        .sum()
        .reset_index(name="total_region_convocatoria")
    )

    participacion_clasif_conv = clasif_region_conv.merge(
        total_region_conv,
        on=["NME_REGION_GR", "ID_CONVOCATORIA"],
        how="left"
    )

    participacion_clasif_conv["participacion_clasificacion_region_convocatoria_pct"] = (
        participacion_clasif_conv["produccion_total"]
        / participacion_clasif_conv["total_region_convocatoria"]
        * 100
    ).round(4)

    indicadores["16_participacion_clasificacion_region_convocatoria_match.csv"] = save_csv(
        participacion_clasif_conv,
        "16_participacion_clasificacion_region_convocatoria_match.csv"
    )

    return indicadores


def table_to_html(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Convierte una tabla a HTML mostrando solo las primeras filas para que el reporte sea legible.
    """
    if df.empty:
        return "<p>No hay registros para mostrar.</p>"

    return df.head(max_rows).to_html(
        index=False,
        border=0,
        classes="data-table",
        escape=True
    )


def generar_html(indicadores: dict[str, pd.DataFrame], df: pd.DataFrame, parquet_path: Path) -> None:
    """
    Genera un HTML de evidencia con fórmulas, explicación y primeras filas de cada indicador.
    """
    html_path = DOCS_DIR / "indicadores_issue43.html"

    formulas = [
        {
            "archivo": "01_produccion_total_region_match.csv",
            "indicador": "Producción total por región",
            "formula": "Pᵣ = Σ 1",
            "interpretacion": "Cuenta el número total de productos científicos asociados a cada región."
        },
        {
            "archivo": "02_participacion_region_match.csv",
            "indicador": "Participación porcentual regional",
            "formula": "%ᵣ = (Pᵣ / Pₜ) × 100",
            "interpretacion": "Mide el peso relativo de cada región frente al total nacional."
        },
        {
            "archivo": "03_promedio_por_grupo_match.csv",
            "indicador": "Producción promedio por grupo",
            "formula": "Promᵣ = Pᵣ / Gᵣ",
            "interpretacion": "Calcula la producción media por grupo de investigación en cada región."
        },
        {
            "archivo": "04_produccion_clasificacion_region_match.csv",
            "indicador": "Producción por clasificación del grupo",
            "formula": "Pᵣ,𝒸 = número de productos de la región r asociados a grupos de clasificación c",
            "interpretacion": "Permite observar cómo se distribuye la producción regional según clasificación del grupo."
        },
        {
            "archivo": "05_diversidad_region_match.csv",
            "indicador": "Diversidad de producción científica",
            "formula": "Dᵣ = |Tᵣ|",
            "interpretacion": "Cuenta el número de tipologías distintas de productos en cada región."
        },
        {
            "archivo": "06_indice_especializacion_productiva_match.csv",
            "indicador": "Índice de especialización productiva",
            "formula": "IEᵣ,ₜ = (Pᵣ,ₜ / Pᵣ) / (Pₜ / Pₜₒₜₐₗ)",
            "interpretacion": "Identifica tipologías con mayor concentración relativa en una región frente al patrón nacional."
        },
        {
            "archivo": "07_diversidad_relativa_region_match.csv",
            "indicador": "Diversidad relativa regional",
            "formula": "DRᵣ = Dᵣ / Pᵣ",
            "interpretacion": "Relaciona la diversidad de tipologías con el volumen total de producción regional."
        },
        {
            "archivo": "08_permanencia_grupos_region_match.csv",
            "indicador": "Permanencia de grupos por región",
            "formula": "PGᵣ = grupos presentes en dos o más convocatorias",
            "interpretacion": "Mide continuidad de los grupos de investigación entre convocatorias."
        },
        {
            "archivo": "09_crecimiento_grupos_region_match.csv",
            "indicador": "Crecimiento de grupos por región",
            "formula": "Crecimiento = ((Gₜ - Gₜ₋₁) / Gₜ₋₁) × 100",
            "interpretacion": "Calcula la variación porcentual de grupos entre convocatorias."
        },
        {
            "archivo": "10_consolidacion_grupos_region_match.csv",
            "indicador": "Consolidación de grupos por región",
            "formula": "CGᵣ = grupos permanentes / grupos únicos",
            "interpretacion": "Resume la estabilidad de los grupos en cada región."
        },
        {
            "archivo": "11_renovacion_grupos_region_match.csv",
            "indicador": "Renovación de grupos por región",
            "formula": "RGᵣ,ₜ = grupos cuya primera aparición ocurre en la convocatoria t",
            "interpretacion": "Identifica aparición de grupos nuevos por región y convocatoria."
        },
        {
            "archivo": "12_genero_region_match.csv",
            "indicador": "Distribución por género y región",
            "formula": "% géneroᵣ = registros del género en región / total regional × 100",
            "interpretacion": "Caracteriza la composición por género cuando el cruce con investigadores es válido."
        },
        {
            "archivo": "13_evolucion_grupos_detalle_match.csv",
            "indicador": "Evolución detallada de grupos",
            "formula": "Gᵣ,ₜ = grupos únicos por región y convocatoria",
            "interpretacion": "Presenta grupos y productos por región y convocatoria."
        },
        {
            "archivo": "14_evolucion_grupos_region_match.csv",
            "indicador": "Evolución de grupos por región",
            "formula": "Variación = G última convocatoria - G primera convocatoria",
            "interpretacion": "Resume cambios en el número de grupos entre convocatorias."
        },
        {
            "archivo": "15_participacion_clasificacion_region_match.csv",
            "indicador": "Participación por clasificación del grupo",
            "formula": "% clasificaciónᵣ = productos de clasificación c en región / total regional × 100",
            "interpretacion": "Mide la composición regional según clasificación del grupo."
        },
        {
            "archivo": "16_participacion_clasificacion_region_convocatoria_match.csv",
            "indicador": "Participación por clasificación, región y convocatoria",
            "formula": "% clasificaciónᵣ,ₜ = productos de clasificación c en región y convocatoria / total región-convocatoria × 100",
            "interpretacion": "Permite comparar la composición por clasificación en el tiempo."
        },
    ]

    cards = []
    for item in formulas:
        archivo = item["archivo"]
        df_ind = indicadores.get(archivo, pd.DataFrame())

        cards.append(f"""
        <section class="card">
            <h2>{html.escape(item["indicador"])}</h2>
            <p><strong>Archivo generado:</strong> <code>outputs/indicadores/{html.escape(archivo)}</code></p>
            <p><strong>Fórmula:</strong> <span class="formula">{html.escape(item["formula"])}</span></p>
            <p><strong>Interpretación:</strong> {html.escape(item["interpretacion"])}</p>
            {table_to_html(df_ind)}
        </section>
        """)

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Issue #43 - Indicadores regionales</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
            margin: 0;
            padding: 0;
        }}
        header {{
            background: #102a43;
            color: white;
            padding: 28px 40px;
        }}
        header h1 {{
            margin: 0;
            font-size: 30px;
        }}
        header p {{
            margin: 8px 0 0;
            color: #d9e2ec;
        }}
        main {{
            max-width: 1180px;
            margin: 24px auto;
            padding: 0 20px 40px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi {{
            background: white;
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}
        .kpi .value {{
            font-size: 26px;
            font-weight: bold;
            color: #0b5cad;
        }}
        .kpi .label {{
            font-size: 13px;
            color: #52606d;
            margin-top: 5px;
        }}
        .card {{
            background: white;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 22px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}
        h2 {{
            color: #102a43;
            border-bottom: 1px solid #d9e2ec;
            padding-bottom: 8px;
        }}
        code {{
            background: #eef2f7;
            padding: 2px 6px;
            border-radius: 5px;
        }}
        .formula {{
            font-weight: bold;
            color: #0b5cad;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 14px;
            font-size: 13px;
        }}
        .data-table th {{
            background: #102a43;
            color: white;
            text-align: left;
            padding: 8px;
        }}
        .data-table td {{
            border-bottom: 1px solid #d9e2ec;
            padding: 8px;
        }}
        .note {{
            background: #e8f4ff;
            border-left: 5px solid #0b5cad;
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Issue #43 - Cálculo de indicadores regionales</h1>
        <p>Producción científica registrada en Minciencias · Convocatorias 2017, 2019 y 2021</p>
    </header>

    <main>
        <div class="note">
            <strong>Fuente utilizada:</strong> <code>{html.escape(str(parquet_path.relative_to(BASE_DIR)))}</code><br>
            <strong>Criterio territorial principal:</strong> región del grupo de investigación, variable <code>NME_REGION_GR</code>.
        </div>

        <section class="summary">
            <div class="kpi">
                <div class="value">{len(df):,}</div>
                <div class="label">Registros en la base</div>
            </div>
            <div class="kpi">
                <div class="value">{df["NME_REGION_GR"].nunique():,}</div>
                <div class="label">Regiones identificadas</div>
            </div>
            <div class="kpi">
                <div class="value">{df["COD_GRUPO_GR"].nunique():,}</div>
                <div class="label">Grupos únicos</div>
            </div>
            <div class="kpi">
                <div class="value">{df["ID_CONVOCATORIA"].nunique():,}</div>
                <div class="label">Convocatorias</div>
            </div>
        </section>

        {''.join(cards)}
    </main>
</body>
</html>
    """

    html_path.write_text(html_content, encoding="utf-8")
    print(f"HTML generado: {html_path}")


def main() -> None:
    parquet_path = find_parquet_path()

    print(f"Leyendo base consolidada desde: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    df = normalize_columns(df)
    df = clean_base(df)

    indicadores = calcular_indicadores(df)
    generar_html(indicadores, df, parquet_path)

    print("\nProceso finalizado correctamente.")
    print(f"Indicadores generados en: {OUTPUT_DIR}")
    print(f"HTML generado en: {DOCS_DIR / 'indicadores_issue43.html'}")


if __name__ == "__main__":
    main()
