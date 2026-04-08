from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_FILE = Path("datos/raw/investigadores_consolidado.xlsx")
OUTPUT_FILE = Path("datos/processed/investigadores_limpio.csv")


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"No se encontro el archivo de entrada: {RAW_FILE}")

    df = pd.read_excel(RAW_FILE)
    print("Datos cargados correctamente")
    print(df.shape)
    print(df.columns)
    print(df.describe(include="all"))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Archivo procesado guardado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
