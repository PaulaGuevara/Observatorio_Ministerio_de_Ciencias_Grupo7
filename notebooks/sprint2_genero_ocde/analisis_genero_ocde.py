"""
Análisis de género por gran área OCDE
Sprint 2 — Observatorio MinCiencias 2026-I
Autor: Victor-Diaz-Usta

Objetivo: Evolución de la brecha de género en cada gran área OCDE
          entre convocatorias 2017, 2019 y 2021.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import numpy as np
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
OUT_DIR = ROOT / "artifacts" / "sprint2_genero_ocde"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Paleta y estilo ─────────────────────────────────────────────────────────
COLORES_ANIO = {2017: "#4C72B0", 2019: "#DD8452", 2021: "#55A868"}
COLORES_GENERO = {"Masculino": "#4C72B0", "Femenino": "#DD8452"}
sns.set_theme(style="whitegrid", font_scale=1.1)

# ── 1. Carga y limpieza ─────────────────────────────────────────────────────
print("Cargando datos...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"  {len(df):,} registros - {df['ID_PERSONA_PR'].nunique():,} investigadores unicos")

cols = ["ANO_CONVO", "NME_GRAN_AREA_PR", "NME_GENERO_PR"]
df = df[cols].dropna()

# Estandarizar géneros (solo Masculino / Femenino)
df = df[df["NME_GENERO_PR"].isin(["Masculino", "Femenino"])]
# ANO_CONVO puede venir como año (2017) o como fecha ("12/05/2017")
df["ANO_CONVO"] = pd.to_datetime(df["ANO_CONVO"], dayfirst=True, errors="coerce").dt.year.fillna(
    pd.to_numeric(df["ANO_CONVO"], errors="coerce")
).astype(int)

print(f"  Registros con género válido: {len(df):,}")
print(f"  Años disponibles: {sorted(df['ANO_CONVO'].unique())}")
print(f"  Grandes áreas: {df['NME_GRAN_AREA_PR'].nunique()}")
print()

# ── 2. Tabla base: conteos y porcentajes por área y año ─────────────────────
tabla = (
    df.groupby(["ANO_CONVO", "NME_GRAN_AREA_PR", "NME_GENERO_PR"])
    .size()
    .reset_index(name="N")
)
total = tabla.groupby(["ANO_CONVO", "NME_GRAN_AREA_PR"])["N"].transform("sum")
tabla["pct"] = tabla["N"] / total * 100

# Tabla pivot: % femenino por área y año
pct_fem = (
    tabla[tabla["NME_GENERO_PR"] == "Femenino"]
    .pivot(index="NME_GRAN_AREA_PR", columns="ANO_CONVO", values="pct")
    .fillna(0)
    .sort_values(2021)
)

# Brecha de género (% masc - % fem)
pct_masc = (
    tabla[tabla["NME_GENERO_PR"] == "Masculino"]
    .pivot(index="NME_GRAN_AREA_PR", columns="ANO_CONVO", values="pct")
    .fillna(0)
)
brecha = pct_masc - (100 - pct_masc)  # = %masc - %fem

print("-- % Femenino por Gran Area OCDE --")
print(pct_fem.round(1).to_string())
print()
print("-- Cambio 2017 a 2021 (puntos porcentuales) --")
cambio = (pct_fem[2021] - pct_fem[2017]).round(2).sort_values(ascending=False)
print(cambio.to_string())
print()

# ── 3. Figura 1: Barras agrupadas — % femenino por área y año ──────────────
areas = pct_fem.index.tolist()
x = np.arange(len(areas))
anios = [2017, 2019, 2021]
width = 0.25

fig, ax = plt.subplots(figsize=(12, 6))
for i, anio in enumerate(anios):
    valores = pct_fem[anio].values if anio in pct_fem.columns else np.zeros(len(areas))
    bars = ax.bar(x + i * width, valores, width, label=str(anio),
                  color=COLORES_ANIO[anio], alpha=0.85, edgecolor="white")
    for bar, val in zip(bars, valores):
        if val > 2:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=7.5, fontweight="bold")

ax.axhline(50, color="red", linestyle="--", linewidth=1.2, alpha=0.6, label="Paridad (50%)")
ax.set_xticks(x + width)
ax.set_xticklabels(areas, rotation=25, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, 75)
ax.set_ylabel("% Investigadoras mujeres")
ax.set_title("Representación femenina por gran área OCDE\nConvocatorias 2017, 2019 y 2021", fontsize=13)
ax.legend(title="Año", loc="upper left")
fig.tight_layout()
fig.savefig(OUT_DIR / "fig1_barras_pct_femenino.png", dpi=150)
plt.close(fig)
print("Figura 1 guardada.")

# ── 4. Figura 2: Heatmap % femenino ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(
    pct_fem.T,
    annot=True, fmt=".1f", cmap="RdYlGn",
    vmin=20, vmax=60,
    linewidths=0.5, linecolor="white",
    cbar_kws={"label": "% Femenino", "format": "%.0f%%"},
    ax=ax,
)
ax.set_xlabel("")
ax.set_ylabel("Año")
ax.set_title("Heatmap: % investigadoras mujeres por gran área OCDE y año", fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig2_heatmap_pct_femenino.png", dpi=150)
plt.close(fig)
print("Figura 2 guardada.")

# ── 5. Figura 3: Líneas — evolución temporal por área ───────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
paleta = sns.color_palette("tab10", n_colors=len(pct_fem))
for area, color in zip(pct_fem.index, paleta):
    valores = [pct_fem.loc[area, a] if a in pct_fem.columns else np.nan for a in anios]
    ax.plot(anios, valores, marker="o", linewidth=2, color=color, label=area)
    ax.text(2021.1, valores[-1], f"  {area}", va="center", fontsize=8, color=color)

ax.axhline(50, color="red", linestyle="--", linewidth=1.2, alpha=0.5, label="Paridad (50%)")
ax.set_xticks(anios)
ax.set_xlim(2016.5, 2022.5)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel("% Investigadoras mujeres")
ax.set_title("Evolución de la representación femenina por gran área OCDE\n2017 → 2021", fontsize=13)
ax.legend(loc="lower left", fontsize=7.5, title="Gran área", ncol=2)
fig.tight_layout()
fig.savefig(OUT_DIR / "fig3_lineas_evolucion.png", dpi=150)
plt.close(fig)
print("Figura 3 guardada.")

# ── 6. Figura 4: Brecha de género (% masc - % fem) ──────────────────────────
brecha_sorted = brecha.sort_values(2021, ascending=True)
anios_disponibles = [a for a in anios if a in brecha_sorted.columns]

fig, ax = plt.subplots(figsize=(10, 6))
for i, anio in enumerate(anios_disponibles):
    ax.barh(
        np.arange(len(brecha_sorted)) + i * 0.25,
        brecha_sorted[anio],
        height=0.25,
        label=str(anio),
        color=COLORES_ANIO[anio],
        alpha=0.85,
    )

ax.axvline(0, color="black", linewidth=0.8)
ax.set_yticks(np.arange(len(brecha_sorted)) + 0.25)
ax.set_yticklabels(brecha_sorted.index, fontsize=9)
ax.set_xlabel("Brecha de género (% Masculino − % Femenino)")
ax.set_title("Brecha de género por gran área OCDE\nConvocatorias 2017, 2019 y 2021", fontsize=13)
ax.legend(title="Año")
fig.tight_layout()
fig.savefig(OUT_DIR / "fig4_brecha_genero.png", dpi=150)
plt.close(fig)
print("Figura 4 guardada.")

# ── 7. Exportar tabla resumen ────────────────────────────────────────────────
resumen = pct_fem.copy()
resumen.columns = [f"pct_fem_{a}" for a in resumen.columns]
resumen["cambio_2017_2021"] = resumen.get("pct_fem_2021", 0) - resumen.get("pct_fem_2017", 0)
resumen = resumen.round(2).reset_index()
resumen.to_csv(OUT_DIR / "tabla_pct_femenino_por_area_anio.csv", index=False)
print("Tabla CSV exportada.")

print(f"\nTodos los artefactos guardados en: {OUT_DIR}")
