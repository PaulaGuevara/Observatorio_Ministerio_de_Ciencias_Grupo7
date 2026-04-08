from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Any

from sodapy import Socrata


DATASETS = {
    "2017": "7669-9v24",
    "2019": "853n-fj7y",
    "2021": "bqtm-4y2h",
}

DOMAIN = "www.datos.gov.co"
RAW_DIR = Path("datos") / "raw"


def fetch_dataset(dataset_id: str, limit: int, offset_step: int) -> list[dict[str, Any]]:
    """Descarga un dataset completo por paginacion."""
    token = os.getenv("SOCRATA_APP_TOKEN")
    client = Socrata(DOMAIN, token, timeout=60)

    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        batch = client.get(dataset_id, limit=limit, offset=offset)
        if not batch:
            break
        rows.extend(batch)
        offset += offset_step
    client.close()
    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Guarda filas en CSV respetando todas las columnas disponibles."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_ingestion(limit: int = 50000) -> None:
    """Descarga datasets 2017, 2019 y 2021 de investigadores."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for year, dataset_id in DATASETS.items():
        print(f"Descargando convocatoria {year} ({dataset_id})...")
        rows = fetch_dataset(dataset_id=dataset_id, limit=limit, offset_step=limit)
        output_path = RAW_DIR / f"investigadores_{year}.csv"
        write_csv(rows, output_path)
        print(f"Guardado: {output_path} ({len(rows)} filas)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingesta de datasets de Minciencias desde datos.gov.co usando sodapy."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50000,
        help="Tamano del lote de paginacion para la API Socrata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_ingestion(limit=args.limit)


if __name__ == "__main__":
    main()
