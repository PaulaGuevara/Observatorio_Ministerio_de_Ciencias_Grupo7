import json
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Polygon

repo = Path(r"c:/Users/USUARIO/Downloads/Propuesta excel(5)/Observatorio_Ministerio_de_Ciencias_Grupo7")
img_dir = repo / "docs" / "informe" / "imagenes"
geo_path = repo / "datos" / "processed" / "co.json"
prod_path = repo / "datos" / "processed" / "indicadores" / "01b_produccion_total_region_convocatoria_match.csv"
base_path = repo / "datos" / "tarea_join" / "investigadores_consolidado.csv"


def norm(text):
    if text is None:
        return ""
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.upper()


with open(geo_path, encoding="utf-8") as file_handle:
    geo = json.load(file_handle)

base = pd.read_csv(base_path, usecols=["NME_DEPARTAMENTO_RES_PR", "NME_REGION_RES_PR"])
base = base.dropna()
base["dept_norm"] = base["NME_DEPARTAMENTO_RES_PR"].map(norm)
base["region"] = base["NME_REGION_RES_PR"].astype(str).str.strip()
map_df = (
    base.groupby(["dept_norm", "region"]).size().reset_index(name="n")
    .sort_values(["dept_norm", "n"], ascending=[True, False])
    .groupby("dept_norm")
    .head(1)
)
dep_to_region = dict(zip(map_df["dept_norm"], map_df["region"]))

aliases = {
    "DISTRITO CAPITAL DE BOGOTA": "BOGOTA, D. C.",
    "SAN ANDRES Y PROVIDENCIA": "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA",
}

rows = []
for feature in geo["features"]:
    name = feature["properties"]["name"]
    name_norm = norm(name)
    lookup = aliases.get(name_norm, name_norm)
    rows.append({
        "departamento": name,
        "dept_norm": lookup,
        "region": dep_to_region.get(lookup),
    })
geo_df = pd.DataFrame(rows)
region_lookup = dict(zip(geo_df["departamento"], geo_df["region"]))


def iter_outer_rings(feature):
    geometry = feature["geometry"]
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"][0]
        return

    if geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield polygon[0]

prod = pd.read_csv(prod_path)
for year in [2017, 2019, 2021]:
    year_df = prod[prod["ANIO_CONVOCATORIA"] == year].copy()
    region_vals = dict(zip(year_df["NME_REGION_GR"], year_df["produccion_total"]))
    patches = []
    values = []
    x_coords = []
    y_coords = []

    for feature in geo["features"]:
        dept_name = feature["properties"]["name"]
        region = region_lookup.get(dept_name)
        value = region_vals.get(region)
        if value is None:
            continue

        for ring in iter_outer_rings(feature):
            xy = [(point[0], point[1]) for point in ring]
            patches.append(Polygon(xy, closed=True))
            values.append(value)
            x_coords.extend(point[0] for point in ring)
            y_coords.extend(point[1] for point in ring)

    norm_scale = Normalize(vmin=min(values), vmax=max(values))
    cmap = plt.cm.YlOrRd
    figure, axis = plt.subplots(figsize=(12, 12))
    collection = PatchCollection(
        patches,
        cmap=cmap,
        norm=norm_scale,
        edgecolor="white",
        linewidth=0.7,
    )
    collection.set_array(pd.Series(values))
    axis.add_collection(collection)
    axis.set_xlim(min(x_coords) - 1, max(x_coords) + 1)
    axis.set_ylim(min(y_coords) - 1, max(y_coords) + 1)
    axis.set_aspect("equal")
    axis.set_axis_off()
    axis.set_title(f"Mapa regional real por departamentos - Producción total {year}", fontsize=20, pad=18)

    colorbar = figure.colorbar(ScalarMappable(norm=norm_scale, cmap=cmap), ax=axis, fraction=0.03, pad=0.02)
    colorbar.set_label("Producción total", fontsize=14)

    output_path = img_dir / f"dashboard_mapa_produccion_{year}.png"
    figure.tight_layout()
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(figure)
    print(f"saved {output_path.name}")
