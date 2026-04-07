from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
from pyvis.network import Network


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
OUTPUT_HTML = PROJECT_ROOT / "hallazgos" / "sprint_3_cofiliacion_grafo_interactivo.html"


def split_affiliations(raw_value: str) -> list[str]:
    cleaned = (raw_value or "").strip()
    if not cleaned:
        return []

    parts = [item.strip() for item in cleaned.split("|")]
    parts = [" ".join(item.split()) for item in parts if item and item.upper() != "NA"]

    dedup: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = part.casefold()
        if key not in seen:
            dedup.append(part)
            seen.add(key)
    return dedup


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def canonical_institution_name(value: str) -> str:
    text = " ".join(value.split())
    text = text.upper()

    parenthetical = re.search(r"\(([^)]+)\)", text)
    if parenthetical:
        inside = " ".join(parenthetical.group(1).split())
        if any(token in inside for token in ["UNIVERSIDAD", "INSTITUTO", "FUNDACION", "ESCUELA", "CORPORACION"]):
            text = inside

    text = re.sub(r"\s*-\s*SEDE\s+.*$", "", text)
    text = re.sub(r"\s+SEDE\s+.*$", "", text)
    text = re.sub(r"\s+UNIGUAJIRA$", "", text)
    text = re.sub(r"\s+UPTC$", "", text)
    text = re.sub(r"\s+\([^)]*\)", "", text)
    text = re.sub(r"[^A-Z0-9 ]+", " ", strip_accents(text))
    text = " ".join(text.split())
    return text


def build_network(path: Path, min_shared: int) -> nx.Graph:
    node_people: Counter[str] = Counter()
    edge_shared_people: Counter[tuple[str, str]] = Counter()
    display_name_by_canonical: dict[str, Counter[str]] = {}

    with path.open("r", encoding="latin-1", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            raw_affiliations = split_affiliations(row.get("INST_FILIA") or "")
            if not raw_affiliations:
                continue

            canonical_affiliations: list[str] = []
            seen_in_person: set[str] = set()
            for raw_name in raw_affiliations:
                canonical = canonical_institution_name(raw_name)
                if not canonical:
                    continue

                if canonical not in seen_in_person:
                    canonical_affiliations.append(canonical)
                    seen_in_person.add(canonical)

                if canonical not in display_name_by_canonical:
                    display_name_by_canonical[canonical] = Counter()
                display_name_by_canonical[canonical][raw_name] += 1

            if not canonical_affiliations:
                continue

            for institution in canonical_affiliations:
                node_people[institution] += 1

            if len(canonical_affiliations) < 2:
                continue

            for left, right in combinations(sorted(canonical_affiliations, key=str.casefold), 2):
                edge_shared_people[(left, right)] += 1

    graph = nx.Graph()
    for institution, people in node_people.items():
        display_counter = display_name_by_canonical.get(institution, Counter())
        display_name = display_counter.most_common(1)[0][0] if display_counter else institution
        graph.add_node(institution, researchers=people, display_name=display_name)

    for (left, right), shared in edge_shared_people.items():
        if shared >= min_shared:
            graph.add_edge(left, right, weight=shared)

    graph.remove_nodes_from([node for node in graph.nodes if graph.degree(node) == 0])
    return graph


def render_pyvis_html(graph: nx.Graph, output_path: Path, min_shared: int = 2) -> None:
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#f5f1e8",
        font_color="#1a1a1a",
        notebook=False,
        directed=False,
    )

    net.barnes_hut(gravity=-25000, central_gravity=0.25, spring_length=180, spring_strength=0.015)

    for node in graph.nodes:
        label = str(graph.nodes[node].get("display_name", node))
        researchers = int(graph.nodes[node].get("researchers", 0))
        strength = int(graph.degree(node, weight="weight"))
        size = 12 + min(50, researchers**0.55)

        net.add_node(
            node,
            label=label,
            size=size,
            color="#0f766e",
            borderWidth=2,
            borderWidthSelected=4,
            title=(
                f"<b>{label}</b><br>"
                f"Investigadores afiliados: {researchers}<br>"
                f"Peso total de conexiones: {strength}"
            ),
            font={"size": 14, "face": "Georgia"},
        )

    for left, right, data in graph.edges(data=True):
        shared = int(data.get("weight", 0))
        width = 1.5 + min(12, shared / 2.5)
        net.add_edge(
            left,
            right,
            value=shared,
            width=width,
            color={
                "color": "#b45309",
                "highlight": "#d97706",
                "hover": "#d97706",
            },
            title=f"Investigadores compartidos: {shared}",
        )

    net.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "scaling": {
              "label": {"enabled": true, "min": 14, "max": 28},
              "min": 12,
              "max": 50
            },
            "font": {
              "size": 16,
              "face": "Georgia",
              "color": "#ffffff",
              "strokeWidth": 0
            },
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.2)",
              "size": 8,
              "x": 4,
              "y": 4
            }
          },
          "edges": {
            "smooth": {"enabled": true, "type": "continuous"},
            "color": {"inherit": false},
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.15)",
              "size": 6,
              "x": 2,
              "y": 2
            }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "tooltipDelay": 100,
            "zoomView": true,
            "dragView": true
          },
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -25000,
              "centralGravity": 0.25,
              "springConstant": 0.015,
              "springLength": 180,
              "damping": 0.7
            },
            "stabilization": {
              "enabled": true,
              "iterations": 500,
              "fit": true,
              "updateInterval": 50
            }
          }
        }
        """
    )

    html_content = net.generate_html()
    
    header = f'<div style="background: linear-gradient(135deg, rgba(15, 118, 110, 0.95), rgba(30, 36, 48, 0.96)); color: white; padding: 20px 40px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);"><h1 style="margin: 0; font-size: 28px;">Sprint 3 #18 - Visualización interactiva de co-filiación</h1><p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.95;">Grafo de instituciones conectadas por investigadores compartidos (INST_FILIA)</p></div>'
    
    info = f'<div style="padding: 20px 40px; background: white; border-bottom: 1px solid #e0dbd0; font-size: 14px; color: #555;"><strong style="color: #0f766e;">Instrucciones:</strong> Usa el mouse para arrastrar nodos, zoom, navegar. Haz clic en una institución para resaltarla. Umbral mínimo de investigadores compartidos por arista: <strong>{min_shared}</strong></div>'
    
    final_html = html_content.replace('<body>', header + info + '\n<body>').replace('height: 100vh', 'height: calc(100vh - 160px)')
    
    output_path.write_text(final_html, encoding="utf-8")


def main() -> None:
    min_shared = 2

    graph = build_network(DATA_PATH, min_shared=min_shared)

    print(f"Grafo construido:")
    print(f"  - Nodos (instituciones): {graph.number_of_nodes()}")
    print(f"  - Aristas (co-filiaciones): {graph.number_of_edges()}")
    print(f"  - Densidad: {nx.density(graph) if graph.number_of_nodes() > 1 else 0.0:.6f}")

    render_pyvis_html(graph, OUTPUT_HTML, min_shared=min_shared)

    print(f"\nHTML interactivo generado en: {OUTPUT_HTML}")
    print(f"Abre en tu navegador: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
