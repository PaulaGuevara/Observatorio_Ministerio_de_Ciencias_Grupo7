from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "resultados_minciencias"


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figuras").mkdir(parents=True, exist_ok=True)
    (output_dir / "tablas").mkdir(parents=True, exist_ok=True)
    return output_dir


def read_any_table(path: Path) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    suffix = path.suffix.lower()
    if suffix == ".csv":
        tables[path.stem] = pd.read_csv(path, low_memory=False)
    elif suffix in {".xlsx", ".xls"}:
        excel_book = pd.ExcelFile(path)
        for sheet_name in excel_book.sheet_names:
            table_name = f"{path.stem}__{sheet_name}"
            tables[table_name] = pd.read_excel(excel_book, sheet_name=sheet_name)
    return tables


def find_existing(paths: Iterable[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No se encontró ningún archivo en las rutas esperadas. "
        "Ajusta rutas de entrada en argumentos o mueve los datos al proyecto."
    )


def build_consolidated_base(output_dir: Path) -> pd.DataFrame:
    candidates = [
        PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv",
        PROJECT_ROOT / "datos" / "tarea_join" / "Investigadores_Consolidado.csv",
        PROJECT_ROOT / "Investigadores_Consolidado.csv",
    ]
    existing_path = next((path for path in candidates if path.exists()), None)
    if existing_path is not None:
        consolidated = pd.read_csv(existing_path, low_memory=False)
    else:
        csv_candidates = list(PROJECT_ROOT.rglob("*Investigadores_Reconocidos*.csv"))
        if len(csv_candidates) == 0:
            raise FileNotFoundError(
                "No se encontró base consolidada ni archivos por convocatoria para construirla."
            )
        dataframes = [pd.read_csv(path, low_memory=False) for path in csv_candidates]
        consolidated = pd.concat(dataframes, ignore_index=True)

    consolidated.to_csv(output_dir / "Investigadores_Consolidado.csv", index=False)
    consolidated.to_excel(output_dir / "Investigadores_Consolidado.xlsx", index=False)
    return consolidated


def deduplicate_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    if "ID_PERSONA_PR" not in df.columns or "ID_CONVOCATORIA" not in df.columns:
        return df.copy()

    convocatoria_priority = {21: 3, 20: 2, 19: 1}
    deduplicated = (
        df.assign(
            _priority=df["ID_CONVOCATORIA"].map(convocatoria_priority).fillna(0),
            _id=df["ID_PERSONA_PR"].astype(str),
        )
        .sort_values(["_id", "_priority"], ascending=[True, False])
        .drop_duplicates(subset=["_id"], keep="first")
        .drop(columns=["_priority", "_id"])
    )
    return deduplicated


def create_dimensions_and_fact(consolidated_df: pd.DataFrame, output_dir: Path) -> dict[str, pd.DataFrame]:
    dimensions: dict[str, pd.DataFrame] = {}

    if "ID_PERSONA_PR" in consolidated_df.columns:
        dimensions["dimension_investigadores"] = consolidated_df[["ID_PERSONA_PR"]].drop_duplicates()

    convocatoria_cols = [column for column in ["ID_CONVOCATORIA", "NME_CONVOCATORIA", "ANO_CONVO"] if column in consolidated_df.columns]
    if len(convocatoria_cols) > 0:
        dimensions["dimension_convocatoria"] = consolidated_df[convocatoria_cols].drop_duplicates(subset=["ID_CONVOCATORIA"] if "ID_CONVOCATORIA" in convocatoria_cols else None)

    nacimiento_cols = [
        column
        for column in [
            "COD_DANE_NAC_PR",
            "NME_MUNICIPIO_NAC_PR",
            "NME_DEPARTAMENTO_NAC_PR",
            "NME_REGION_NAC_PR",
            "NME_PAIS_NAC_PR",
        ]
        if column in consolidated_df.columns
    ]
    if len(nacimiento_cols) > 0 and "COD_DANE_NAC_PR" in nacimiento_cols:
        dimensions["dimension_municipios_nacimiento"] = consolidated_df[nacimiento_cols].drop_duplicates(subset=["COD_DANE_NAC_PR"])

    for name, dimension_table in dimensions.items():
        dimension_table.to_csv(output_dir / "tablas" / f"{name}.csv", index=False)

    fact_columns_priority = [
        "ID_CONVOCATORIA",
        "ID_PERSONA_PR",
        "ID_GENERO",
        "COD_DANE_NAC_PR",
        "ID_NIV_FORMACION_PR",
        "ID_CLAS_PR",
        "COD_DANE_RES_PR",
        "EDAD_ANOS_PR",
        "NME_GRAN_AREA_PR",
        "NME_GENERO_PR",
        "NME_NIV_FORM_PR",
        "NME_CLASIFICACION_PR",
        "NME_REGION_RES_PR",
        "INST_FILIA",
    ]
    fact_columns = [column for column in fact_columns_priority if column in consolidated_df.columns]
    fact_table = consolidated_df[fact_columns].copy() if len(fact_columns) > 0 else consolidated_df.copy()
    fact_table.to_csv(output_dir / "tablas" / "tabla_hechos.csv", index=False)

    dimensions["tabla_hechos"] = fact_table
    return dimensions


def guess_fact_table_name(tables: dict[str, pd.DataFrame]) -> str:
    lower_names = {name: name.lower() for name in tables}
    fact_candidates = [name for name, lower_name in lower_names.items() if "hecho" in lower_name or "fact" in lower_name]
    if len(fact_candidates) > 0:
        return max(fact_candidates, key=lambda name: len(tables[name]))
    return max(tables, key=lambda name: len(tables[name]))


def candidate_common_keys(dimension_df: pd.DataFrame, base_df: pd.DataFrame) -> list[str]:
    common_cols = [column for column in dimension_df.columns if column in base_df.columns]
    if len(common_cols) == 0:
        return []

    unique_candidates: list[str] = []
    for column in common_cols:
        if dimension_df[column].notna().sum() == 0:
            continue
        is_unique = dimension_df[column].nunique(dropna=True) == len(dimension_df[column].dropna())
        if is_unique:
            unique_candidates.append(column)

    if len(unique_candidates) > 0:
        return [unique_candidates[0]]

    id_like_candidates = [column for column in common_cols if "id" in column.lower() or "cod" in column.lower()]
    if len(id_like_candidates) > 0:
        return [id_like_candidates[0]]

    return [common_cols[0]]


def create_gran_tabla_from_folder(source_folder: Path, output_dir: Path) -> pd.DataFrame:
    all_tables: dict[str, pd.DataFrame] = {}
    for source_file in source_folder.iterdir():
        if source_file.suffix.lower() in {".csv", ".xlsx", ".xls"}:
            all_tables.update(read_any_table(source_file))

    if len(all_tables) == 0:
        raise FileNotFoundError(f"No se detectaron tablas en {source_folder}")

    fact_name = guess_fact_table_name(all_tables)
    gran_tabla = all_tables[fact_name].copy()
    join_log: list[dict[str, object]] = []

    for table_name, table_df in all_tables.items():
        if table_name == fact_name:
            continue

        merge_keys = candidate_common_keys(table_df, gran_tabla)
        if len(merge_keys) == 0:
            join_log.append(
                {
                    "dimension": table_name,
                    "keys": "",
                    "used": False,
                    "note": "Sin llaves comunes",
                }
            )
            continue

        renamed_dimension = table_df.rename(
            columns={column: f"{table_name}__{column}" for column in table_df.columns if column not in merge_keys}
        )
        before_rows = len(gran_tabla)
        merged = gran_tabla.merge(renamed_dimension, how="left", on=merge_keys)

        if len(merged) > before_rows:
            join_log.append(
                {
                    "dimension": table_name,
                    "keys": ",".join(merge_keys),
                    "used": False,
                    "note": "La unión aumentó filas (posible 1:N)",
                }
            )
            continue

        gran_tabla = merged
        join_log.append(
            {
                "dimension": table_name,
                "keys": ",".join(merge_keys),
                "used": True,
                "note": "OK",
            }
        )

    columns_to_remove = {
        "ID_GENERO",
        "ID_AREA_CON_PR",
        "ID_CLAS_PR",
        "UNIVERSIDAD",
        "ID_PERSONA_PR",
        "ID_CONVOCATORIA",
        "COD_DANE_NAC_PR",
        "ID_NIV_FORMACION_PR",
        "COD_DANE_RES_PR",
    }
    gran_tabla_sin_id = gran_tabla.drop(columns=[column for column in gran_tabla.columns if column.upper() in columns_to_remove], errors="ignore")

    pd.DataFrame(join_log).to_csv(output_dir / "tablas" / "reporte_uniones.csv", index=False)
    gran_tabla.to_csv(output_dir / "gran_tabla.csv", index=False)
    gran_tabla_sin_id.to_csv(output_dir / "gran_tabla_sin_id.csv", index=False)

    return gran_tabla_sin_id


def run_univariado(df: pd.DataFrame, output_dir: Path) -> None:
    numeric_candidates = [column for column in ["NRO_ORDEN_FORM_PR", "ORDEN_CLAS_PR", "EDAD_ANOS_PR"] if column in df.columns]
    for column in numeric_candidates:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if len(numeric_candidates) > 0:
        numeric_summary = df[numeric_candidates].describe().transpose()
        numeric_summary["missing_pct"] = df[numeric_candidates].isna().mean() * 100
        numeric_summary.to_csv(output_dir / "tablas" / "univariado_resumen_numericas.csv")

    categorical_columns = [
        column
        for column in [
            "NME_GENERO_PR",
            "NME_GRAN_AREA_PR",
            "NME_REGION_RES_PR",
            "NME_NIV_FORM_PR",
            "NME_CLASIFICACION_PR",
        ]
        if column in df.columns
    ]

    for column in categorical_columns:
        top_freq = df[column].value_counts(dropna=False).head(20)
        top_freq.to_csv(output_dir / "tablas" / f"frecuencia_{column}.csv")

        plt.figure(figsize=(10, 5))
        top_freq.head(10).plot(kind="bar", color="#5DA5DA")
        plt.title(f"Distribución de {column}")
        plt.xlabel(column)
        plt.ylabel("Frecuencia")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(output_dir / "figuras" / f"univariado_{column}.png", dpi=150)
        plt.close()

    if "ANO_CONVO" in df.columns:
        years = pd.to_datetime(df["ANO_CONVO"], errors="coerce", dayfirst=True).dt.year
        if years.notna().sum() == 0:
            years = pd.to_numeric(df["ANO_CONVO"], errors="coerce")
        yearly_counts = years.dropna().astype(int).value_counts().sort_index()
        yearly_counts.to_csv(output_dir / "tablas" / "conteo_anual_convocatoria.csv")

        plt.figure(figsize=(7, 4))
        plt.bar(yearly_counts.index.astype(str), yearly_counts.values, color="#4E79A7")
        plt.title("Investigadores por año de convocatoria")
        plt.xlabel("Año")
        plt.ylabel("Cantidad")
        plt.tight_layout()
        plt.savefig(output_dir / "figuras" / "convocatorias_por_ano.png", dpi=150)
        plt.close()


def run_analisis_2019_style(df: pd.DataFrame, output_dir: Path) -> None:
    missing_stats = (
        df.isna()
        .sum()
        .rename("n_missing")
        .to_frame()
        .assign(pct_missing=lambda table: (100 * table["n_missing"] / len(df)).round(2))
        .sort_values("pct_missing", ascending=False)
    )
    missing_stats.to_csv(output_dir / "tablas" / "faltantes_2019_style.csv")

    top_missing = missing_stats.head(15).iloc[::-1]
    plt.figure(figsize=(10, 6))
    plt.barh(top_missing.index.astype(str), top_missing["pct_missing"], color="#E15759")
    plt.title("Top variables con mayor porcentaje de faltantes")
    plt.xlabel("% faltantes")
    plt.tight_layout()
    plt.savefig(output_dir / "figuras" / "faltantes_top15.png", dpi=150)
    plt.close()

    if {"NME_GRAN_AREA_PR", "NME_GENERO_PR"}.issubset(df.columns):
        crosstab = pd.crosstab(df["NME_GRAN_AREA_PR"], df["NME_GENERO_PR"], normalize="index") * 100
        crosstab.to_csv(output_dir / "tablas" / "gran_area_x_genero_pct.csv")


def run_correspondence_like(df: pd.DataFrame, output_dir: Path) -> None:
    candidate_pairs = [
        ("NME_GRAN_AREA_PR", "NME_GENERO_PR"),
        ("INST_FILIA", "NME_GENERO_PR"),
        ("NME_NIV_FORM_PR", "NME_CLASIFICACION_PR"),
    ]

    for left_column, right_column in candidate_pairs:
        if left_column not in df.columns or right_column not in df.columns:
            continue
        contingency = pd.crosstab(df[left_column], df[right_column])
        contingency.to_csv(output_dir / "tablas" / f"contingencia_{left_column}_x_{right_column}.csv")


def run_clusters(df: pd.DataFrame, output_dir: Path, clusters: int = 3) -> None:
    required_columns = [
        column
        for column in [
            "EDAD_ANOS_PR",
            "NME_GRAN_AREA_PR",
            "NME_GENERO_PR",
            "NME_REGION_RES_PR",
            "NME_NIV_FORM_PR",
            "NME_CLASIFICACION_PR",
        ]
        if column in df.columns
    ]
    if len(required_columns) < 2:
        return

    cluster_df = df[required_columns].copy().dropna()
    if len(cluster_df) == 0:
        return

    numeric_cols = [column for column in cluster_df.columns if pd.api.types.is_numeric_dtype(cluster_df[column])]

    try:
        from kmodes.kprototypes import KPrototypes

        matrix = cluster_df.copy()
        for column in matrix.columns:
            if column not in numeric_cols:
                matrix[column] = matrix[column].astype(str)
        categorical_index = [idx for idx, column in enumerate(matrix.columns) if column not in numeric_cols]

        model = KPrototypes(n_clusters=clusters, init="Cao", n_init=5, random_state=123)
        labels = model.fit_predict(matrix.to_numpy(), categorical=categorical_index)
        cluster_df["cluster"] = labels + 1
        method_used = "kprototypes"
    except Exception:
        encoded = pd.get_dummies(cluster_df, drop_first=False)
        from sklearn.cluster import KMeans

        model = KMeans(n_clusters=clusters, random_state=123, n_init=10)
        labels = model.fit_predict(encoded)
        cluster_df["cluster"] = labels + 1
        method_used = "kmeans_dummy_fallback"

    cluster_df.to_csv(output_dir / "tablas" / "clusters_asignados.csv", index=False)
    cluster_summary = cluster_df.groupby("cluster").agg({column: "mean" for column in numeric_cols if column in cluster_df.columns})
    cluster_summary["n"] = cluster_df["cluster"].value_counts().sort_index()
    cluster_summary["metodo"] = method_used
    cluster_summary.to_csv(output_dir / "tablas" / "clusters_resumen.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline unificado en Python para tareas de notebooks_Minciencias"
    )
    parser.add_argument(
        "--source-folder",
        type=Path,
        default=PROJECT_ROOT / "notebooks_Minciencias",
        help="Carpeta con archivos fuente (csv/xlsx/xls) para construir gran tabla",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Carpeta de salida para tablas y figuras",
    )
    parser.add_argument(
        "--skip-gran-tabla",
        action="store_true",
        help="Si se activa, no intenta construir gran tabla desde carpeta",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = ensure_output_dir(args.output)

    consolidated = build_consolidated_base(output_dir)
    deduplicated = deduplicate_by_priority(consolidated)
    deduplicated.to_csv(output_dir / "Base_sin_duplicados.csv", index=False)

    create_dimensions_and_fact(deduplicated, output_dir)

    if args.skip_gran_tabla:
        working_df = deduplicated.copy()
    else:
        try:
            working_df = create_gran_tabla_from_folder(args.source_folder, output_dir)
        except FileNotFoundError:
            working_df = deduplicated.copy()

    run_univariado(working_df, output_dir)
    run_analisis_2019_style(working_df, output_dir)
    run_correspondence_like(working_df, output_dir)
    run_clusters(working_df, output_dir, clusters=3)

    print("Pipeline finalizado.")
    print(f"Salida disponible en: {output_dir}")


if __name__ == "__main__":
    main()
