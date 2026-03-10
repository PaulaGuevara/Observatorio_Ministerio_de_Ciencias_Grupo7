import pandas as pd
from pathlib import Path

# ruta del archivo
ruta = Path("datos/raw/investigadores_consolidado.xlsx")

# cargar datos
df = pd.read_excel(ruta)

print("Datos cargados correctamente")
print(df.shape)

# ver columnas
print(df.columns)

# estadísticas básicas
print(df.describe())

# guardar versión limpia
df.to_csv("datos/processed/investigadores_limpio.csv", index=False)

print("Archivo procesado guardado")