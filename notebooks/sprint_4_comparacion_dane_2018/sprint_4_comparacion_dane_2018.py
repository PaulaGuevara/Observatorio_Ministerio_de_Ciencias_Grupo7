from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "evidencias" / "sprint4"

# Referencias DANE 2018 usadas para la comparación.
# Ajusta solo estas constantes si el profesor les pide otra fuente o una cifra distinta.
DANE_REFERENCES = {
    "victima_conflicto_pct": 11.80,   # Aproximación de trabajo basada en cruce CNPV 2018 - RUV
    "discapacidad_pct": 4.24,         # DANE CNPV 2018
    "grupo_etnico_pct": {
        "Indígena": 4.40,             # DANE CNPV 2018
        "Rrom": 0.006,                # DANE CNPV 2018
        "NARP": 9.34,                 # DANE, estimación reportada para población NARP
    },
}

TARGET_COLUMNS = [
    "ID_VICTIMA_CONFLICTO",
    "TXT_GRUPO_ETNICO",
    "TXT_POBLACION_DISCA",
]


def ensure_output_dir(output_dir: Path) -> Path:
    """Crea la carpeta de salida y sus subcarpetas."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "tablas").mkdir(parents=True, exist_ok=True)
    (output_dir / "figuras").mkdir(parents=True, exist_ok=True)
    return output_dir


def locate_input_file(user_path: Path | None = None) -> Path:
    """
    Busca la base consolidada en rutas probables del proyecto.
    Si el usuario pasa --input, se usa esa ruta.
    """
    if user_path is not None:
        if not user_path.exists():
            raise FileNotFoundError(f"No existe el archivo indicado: {user_path}")
        return user_path

    candidates = [
        PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv",
        PROJECT_ROOT / "datos" / "tarea_join" / "Investigadores_Consolidado.csv",
        PROJECT_ROOT / "investigadores_consolidado.csv",
        PROJECT_ROOT / "Investigadores_Consolidado.csv",
        PROJECT_ROOT / "resultados_minciencias" / "Investigadores_Consolidado.csv",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "No se encontró la base consolidada. "
        "Usa --input para indicar la ruta exacta del CSV."
    )


def read_base(path: Path) -> pd.DataFrame:
    """Lee la base de entrada."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    raise ValueError(f"Formato no soportado: {suffix}")


def normalize_text(value: object) -> str | None:
    """Normaliza texto para homologar categorías."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if text == "":
        return None

    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    return " ".join(text.split()).upper()


def parse_year(series: pd.Series) -> pd.Series:
    """Extrae el año desde ANO_CONVO, tolerando formatos fecha o texto."""
    years = pd.to_datetime(series, errors="coerce", dayfirst=True).dt.year
    if years.notna().any():
        return years
    return pd.to_numeric(series, errors="coerce")


def is_informative_value(value: object, variable: str) -> bool:
    """
    Determina si un valor es analíticamente útil para Sprint 4.
    """
    text = normalize_text(value)

    if text is None:
        return False

    missing_values = {
        "NO REGISTRA",
        "NO DISPONIBLE",
        "NO INFORMA",
        "SIN INFORMACION",
        "N/R",
        "NR",
        "NA",
        "N/A",
        "NULL",
    }

    if text in missing_values:
        return False

    # Regla adicional por variable si hiciera falta.
    return True


def build_availability_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resume cuánta información útil existe por año y por variable.
    """
    if "ANO_CONVO" not in df.columns:
        raise KeyError("La base no contiene la columna ANO_CONVO.")

    work = df.copy()
    work["ANIO"] = parse_year(work["ANO_CONVO"])

    rows: list[dict[str, object]] = []

    for year, sub in work.groupby("ANIO", dropna=False):
        total = len(sub)

        row: dict[str, object] = {
            "anio": int(year) if pd.notna(year) else None,
            "n_registros": total,
        }

        for column in TARGET_COLUMNS:
            informative_mask = sub[column].apply(lambda x: is_informative_value(x, column))
            row[f"{column}_n_util"] = int(informative_mask.sum())
            row[f"{column}_pct_util"] = round(100 * informative_mask.mean(), 2)

        rows.append(row)

    availability = pd.DataFrame(rows).sort_values("anio")
    return availability


def choose_analysis_year(availability: pd.DataFrame) -> int:
    """
    Escoge el año con mayor disponibilidad conjunta de las tres variables.
    En tu base real será 2021, pero se deja programado de forma general.
    """
    score_cols = [f"{col}_n_util" for col in TARGET_COLUMNS]
    work = availability.copy()
    work["score_total"] = work[score_cols].sum(axis=1)
    best_row = work.sort_values(["score_total", "anio"], ascending=[False, False]).iloc[0]
    return int(best_row["anio"])


def clean_victim(value: object) -> str:
    """Homologa víctima del conflicto a Sí / No / No informa."""
    text = normalize_text(value)

    if text is None:
        return "No informa"

    yes_values = {"SI", "SÍ", "1", "01", "VICTIMA", "VICTIMA DEL CONFLICTO"}
    no_values = {"NO", "0", "00"}

    if text in yes_values:
        return "Sí"
    if text in no_values:
        return "No"
    if text == "NO REGISTRA":
        return "No informa"

    return "No informa"


def clean_ethnicity(value: object) -> str:
    """
    Homologa grupo étnico.
    Se mantiene 'Blanco o mestizo' separado para transparencia,
    pero NO se compara contra DANE por no ser equivalente exacto a 'ningún grupo étnico'.
    """
    text = normalize_text(value)

    if text is None or text == "NO DISPONIBLE":
        return "No informa"

    if "INDIGENA" in text:
        return "Indígena"

    if "RROM" in text or "GITANO" in text:
        return "Rrom"

    if any(token in text for token in [
        "POBLACION NEGRA",
        "AFROCOLOMBIANO",
        "AFRODESCENDIENTE",
        "NEGRO",
        "MULATO",
        "RAIZAL",
        "PALENQUERO",
    ]):
        return "NARP"

    if "BLANCO" in text or "MESTIZO" in text:
        return "Blanco o mestizo"

    if "NINGUN GRUPO ETNICO" in text or "NINGUN" == text:
        return "Ningún grupo étnico"

    return "Otra / por revisar"


def clean_disability_detail(value: object) -> str:
    """Mantiene el detalle de discapacidad, pero normalizado."""
    text = normalize_text(value)

    if text is None or text == "NO DISPONIBLE":
        return "No informa"

    mapping = {
        "NINGUNA": "Ninguna",
        "VISUAL": "Visual",
        "FISICA": "Física",
        "AUDITIVA": "Auditiva",
        "PSICOSOCIAL": "Psicosocial",
        "INTELECTUAL": "Intelectual",
        "MULTIPLE": "Múltiple",
    }

    return mapping.get(text, "Otra / por revisar")


def clean_disability_binary(value: object) -> str:
    """
    Convierte la variable de discapacidad a Sí / No / No informa.
    Todo valor distinto de 'Ninguna' o 'No disponible' cuenta como Sí.
    """
    detail = clean_disability_detail(value)

    if detail == "No informa":
        return "No informa"
    if detail == "Ninguna":
        return "No"

    return "Sí"


def frequency_table(series: pd.Series) -> pd.DataFrame:
    """Calcula frecuencias absolutas y porcentajes sobre el total."""
    table = (
        series.fillna("No informa")
        .value_counts(dropna=False)
        .rename_axis("categoria")
        .reset_index(name="n")
    )
    table["pct_total"] = round(100 * table["n"] / table["n"].sum(), 4)
    return table


def valid_percentage_table(series: pd.Series, missing_labels: set[str]) -> pd.DataFrame:
    """
    Calcula porcentajes excluyendo categorías no informativas del denominador.
    """
    clean = series.copy()
    valid = clean[~clean.isin(missing_labels)]

    if valid.empty:
        return pd.DataFrame(columns=["categoria", "n", "pct_validos"])

    table = (
        valid.value_counts(dropna=False)
        .rename_axis("categoria")
        .reset_index(name="n")
    )
    table["pct_validos"] = round(100 * table["n"] / table["n"].sum(), 4)
    return table


def merge_total_and_valid(total_table: pd.DataFrame, valid_table: pd.DataFrame) -> pd.DataFrame:
    """Une porcentajes sobre total y sobre válidos."""
    merged = total_table.merge(valid_table, on=["categoria", "n"], how="left")
    merged["pct_validos"] = merged["pct_validos"].fillna(0)
    return merged


def save_bar_chart(table: pd.DataFrame, title: str, output_path: Path, pct_column: str) -> None:
    """Guarda un gráfico de barras simple."""
    plt.figure(figsize=(9, 4.8))
    plt.bar(table["categoria"].astype(str), table[pct_column])
    plt.title(title)
    plt.xlabel("Categoría")
    plt.ylabel(pct_column)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def compare_binary(table: pd.DataFrame, dane_pct: float, label: str) -> pd.DataFrame:
    """Compara la categoría 'Sí' contra la referencia DANE."""
    pct_si = float(table.loc[table["categoria"] == "Sí", "pct_validos"].sum())

    return pd.DataFrame(
        {
            "indicador": [label],
            "categoria": ["Sí"],
            "pct_base": [round(pct_si, 4)],
            "pct_dane_2018": [round(dane_pct, 4)],
            "brecha_pp": [round(pct_si - dane_pct, 4)],
        }
    )


def compare_ethnicity(valid_table: pd.DataFrame) -> pd.DataFrame:
    """Compara solo las categorías étnicas que sí tienen referente DANE directo."""
    dane = pd.DataFrame(
        {
            "categoria": ["Indígena", "Rrom", "NARP"],
            "pct_dane_2018": [
                DANE_REFERENCES["grupo_etnico_pct"]["Indígena"],
                DANE_REFERENCES["grupo_etnico_pct"]["Rrom"],
                DANE_REFERENCES["grupo_etnico_pct"]["NARP"],
            ],
        }
    )

    comparison = valid_table.merge(dane, on="categoria", how="inner")
    comparison = comparison.rename(columns={"pct_validos": "pct_base"})
    comparison["brecha_pp"] = round(comparison["pct_base"] - comparison["pct_dane_2018"], 4)

    return comparison[["categoria", "n", "pct_base", "pct_dane_2018", "brecha_pp"]]


def write_markdown_report(
    output_dir: Path,
    input_path: Path,
    analysis_year: int,
    availability: pd.DataFrame,
    victim_table: pd.DataFrame,
    ethnic_table: pd.DataFrame,
    disability_detail_table: pd.DataFrame,
    disability_binary_table: pd.DataFrame,
    comp_victim: pd.DataFrame,
    comp_disability: pd.DataFrame,
    comp_ethnicity: pd.DataFrame,
) -> None:
    """Escribe un borrador de evidencia en Markdown."""
    lines: list[str] = []

    lines.append("# Evidencia Sprint 4")
    lines.append("")
    lines.append("## 1. Fuente de entrada")
    lines.append("")
    lines.append(f"- Archivo analizado: `{input_path}`")
    lines.append(f"- Año seleccionado para la explotación: **{analysis_year}**")
    lines.append("")

    lines.append("## 2. Disponibilidad de variables por año")
    lines.append("")
    lines.append(
        "Se revisaron las convocatorias disponibles y se verificó la disponibilidad "
        "de `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO` y `TXT_POBLACION_DISCA`."
    )
    lines.append("")
    lines.append(availability.to_markdown(index=False))
    lines.append("")

    lines.append("## 3. Justificación metodológica")
    lines.append("")
    lines.append(
        "Aunque el proyecto trabaja con 2017, 2019 y 2021, la explotación sustantiva de estas variables "
        "se realiza sobre el año con información útil. Si en un año los registros aparecen únicamente "
        "como `No registra` o `No disponible`, ese año se documenta, pero no se usa para calcular "
        "porcentajes comparables con DANE."
    )
    lines.append("")

    lines.append("## 4. Resultados descriptivos")
    lines.append("")

    lines.append("### 4.1 Víctima del conflicto")
    lines.append("")
    lines.append(victim_table.to_markdown(index=False))
    lines.append("")

    lines.append("### 4.2 Grupo étnico")
    lines.append("")
    lines.append(ethnic_table.to_markdown(index=False))
    lines.append("")

    lines.append("### 4.3 Discapacidad (detalle)")
    lines.append("")
    lines.append(disability_detail_table.to_markdown(index=False))
    lines.append("")

    lines.append("### 4.4 Discapacidad (binaria)")
    lines.append("")
    lines.append(disability_binary_table.to_markdown(index=False))
    lines.append("")

    lines.append("## 5. Comparación con DANE 2018")
    lines.append("")
    lines.append("### 5.1 Víctima del conflicto")
    lines.append("")
    lines.append(comp_victim.to_markdown(index=False))
    lines.append("")

    lines.append("### 5.2 Discapacidad")
    lines.append("")
    lines.append(comp_disability.to_markdown(index=False))
    lines.append("")

    lines.append("### 5.3 Grupo étnico")
    lines.append("")
    lines.append(comp_ethnicity.to_markdown(index=False))
    lines.append("")

    lines.append("## 6. Conclusión")
    lines.append("")
    lines.append(
        "La comparación se realizó mediante porcentajes y no por conteos absolutos, dado que la base "
        "de investigadores corresponde a una población específica y el DANE 2018 representa la población nacional. "
        "En consecuencia, las brechas se interpretan en puntos porcentuales."
    )
    lines.append("")

    report_path = output_dir / "evidencia_sprint4_variables_dane_2018.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Sprint 4: conflicto, etnia y discapacidad con comparación DANE 2018"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Ruta opcional al CSV consolidado",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Carpeta de salida para evidencias",
    )
    return parser.parse_args()


def main() -> None:
    """Flujo principal del análisis."""
    args = parse_args()
    output_dir = ensure_output_dir(args.output)

    input_path = locate_input_file(args.input)
    df = read_base(input_path)

    missing = [col for col in TARGET_COLUMNS + ["ANO_CONVO"] if col not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas requeridas en la base: {missing}")

    # 1. Diagnóstico de disponibilidad por año.
    availability = build_availability_table(df)
    availability.to_csv(output_dir / "tablas" / "disponibilidad_variables_por_ano.csv", index=False)

    # 2. Selección automática del año con información útil.
    analysis_year = choose_analysis_year(availability)

    work = df.copy()
    work["ANIO"] = parse_year(work["ANO_CONVO"])
    analysis_df = work[work["ANIO"] == analysis_year].copy()

    # 3. Homologación de variables.
    analysis_df["victima_clean"] = analysis_df["ID_VICTIMA_CONFLICTO"].apply(clean_victim)
    analysis_df["etnia_clean"] = analysis_df["TXT_GRUPO_ETNICO"].apply(clean_ethnicity)
    analysis_df["discapacidad_detalle_clean"] = analysis_df["TXT_POBLACION_DISCA"].apply(clean_disability_detail)
    analysis_df["discapacidad_binaria_clean"] = analysis_df["TXT_POBLACION_DISCA"].apply(clean_disability_binary)

    # 4. Tablas descriptivas.
    victim_total = frequency_table(analysis_df["victima_clean"])
    victim_valid = valid_percentage_table(analysis_df["victima_clean"], {"No informa"})
    victim_table = merge_total_and_valid(victim_total, victim_valid)

    ethnic_total = frequency_table(analysis_df["etnia_clean"])
    ethnic_valid = valid_percentage_table(analysis_df["etnia_clean"], {"No informa"})
    ethnic_table = merge_total_and_valid(ethnic_total, ethnic_valid)

    disability_detail_total = frequency_table(analysis_df["discapacidad_detalle_clean"])
    disability_detail_valid = valid_percentage_table(analysis_df["discapacidad_detalle_clean"], {"No informa"})
    disability_detail_table = merge_total_and_valid(disability_detail_total, disability_detail_valid)

    disability_binary_total = frequency_table(analysis_df["discapacidad_binaria_clean"])
    disability_binary_valid = valid_percentage_table(analysis_df["discapacidad_binaria_clean"], {"No informa"})
    disability_binary_table = merge_total_and_valid(disability_binary_total, disability_binary_valid)

    # 5. Guardar tablas.
    victim_table.to_csv(output_dir / "tablas" / "victima_conflicto_frecuencias.csv", index=False)
    ethnic_table.to_csv(output_dir / "tablas" / "grupo_etnico_frecuencias.csv", index=False)
    disability_detail_table.to_csv(output_dir / "tablas" / "discapacidad_detalle_frecuencias.csv", index=False)
    disability_binary_table.to_csv(output_dir / "tablas" / "discapacidad_binaria_frecuencias.csv", index=False)

    # 6. Comparación con DANE.
    comp_victim = compare_binary(
        victim_table,
        DANE_REFERENCES["victima_conflicto_pct"],
        "víctima del conflicto",
    )
    comp_disability = compare_binary(
        disability_binary_table,
        DANE_REFERENCES["discapacidad_pct"],
        "discapacidad",
    )
    comp_ethnicity = compare_ethnicity(ethnic_table)

    comp_victim.to_csv(output_dir / "tablas" / "comparacion_dane_victima_conflicto.csv", index=False)
    comp_disability.to_csv(output_dir / "tablas" / "comparacion_dane_discapacidad.csv", index=False)
    comp_ethnicity.to_csv(output_dir / "tablas" / "comparacion_dane_grupo_etnico.csv", index=False)

    # 7. Gráficos.
    save_bar_chart(
        victim_table,
        f"Víctima del conflicto - {analysis_year}",
        output_dir / "figuras" / "victima_conflicto_pct_validos.png",
        "pct_validos",
    )
    save_bar_chart(
        ethnic_table,
        f"Grupo étnico - {analysis_year}",
        output_dir / "figuras" / "grupo_etnico_pct_validos.png",
        "pct_validos",
    )
    save_bar_chart(
        disability_binary_table,
        f"Discapacidad - {analysis_year}",
        output_dir / "figuras" / "discapacidad_binaria_pct_validos.png",
        "pct_validos",
    )

    # 8. Evidencia en Markdown.
    write_markdown_report(
        output_dir=output_dir,
        input_path=input_path,
        analysis_year=analysis_year,
        availability=availability,
        victim_table=victim_table,
        ethnic_table=ethnic_table,
        disability_detail_table=disability_detail_table,
        disability_binary_table=disability_binary_table,
        comp_victim=comp_victim,
        comp_disability=comp_disability,
        comp_ethnicity=comp_ethnicity,
    )

    print("Sprint 4 ejecutado correctamente.")
    print(f"Archivo de entrada: {input_path}")
    print(f"Año analizado: {analysis_year}")
    print(f"Resultados guardados en: {output_dir}")


if __name__ == "__main__":
    main()