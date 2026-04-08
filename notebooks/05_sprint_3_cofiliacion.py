from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import networkx as nx


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
OUTPUT_MD = PROJECT_ROOT / "hallazgos" / "sprint_3_cofiliacion_network.md"
OUTPUT_EDGES = PROJECT_ROOT / "hallazgos" / "sprint_3_cofiliacion_edges.csv"
OUTPUT_NODES = PROJECT_ROOT / "hallazgos" / "sprint_3_cofiliacion_nodes.csv"
OUTPUT_GEXF = PROJECT_ROOT / "hallazgos" / "sprint_3_cofiliacion_network.gexf"


@dataclass
class NetworkSummary:
    investigators_with_affiliation: int
    investigators_multi_affiliation: int
    institutions_total: int
    edges_total: int
    connected_components: int
    density: float
    top_nodes: list[tuple[str, int, int, float]]
    top_edges: list[tuple[str, str, int]]


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


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


def build_network(path: Path, min_shared: int) -> tuple[nx.Graph, NetworkSummary]:
    people_with_affiliation = 0
    people_multi_affiliation = 0
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

            people_with_affiliation += 1
            for institution in canonical_affiliations:
                node_people[institution] += 1

            if len(canonical_affiliations) < 2:
                continue

            people_multi_affiliation += 1
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

    isolated_nodes = [node for node in graph.nodes if graph.degree(node) == 0]
    graph.remove_nodes_from(isolated_nodes)

    weighted_degree = dict(graph.degree(weight="weight"))
    degree_centrality = nx.degree_centrality(graph) if graph.number_of_nodes() > 1 else {}
    top_nodes = sorted(
        (
            (
                str(graph.nodes[node].get("display_name", node)),
                graph.nodes[node].get("researchers", 0),
                int(weighted_degree.get(node, 0)),
                float(degree_centrality.get(node, 0.0)),
            )
            for node in graph.nodes
        ),
        key=lambda row: (row[2], row[1], row[0].casefold()),
        reverse=True,
    )[:12]

    top_edges = sorted(
        (
            (
                str(graph.nodes[left].get("display_name", left)),
                str(graph.nodes[right].get("display_name", right)),
                int(data.get("weight", 0)),
            )
            for left, right, data in graph.edges(data=True)
        ),
        key=lambda row: (row[2], row[0].casefold(), row[1].casefold()),
        reverse=True,
    )[:15]

    summary = NetworkSummary(
        investigators_with_affiliation=people_with_affiliation,
        investigators_multi_affiliation=people_multi_affiliation,
        institutions_total=graph.number_of_nodes(),
        edges_total=graph.number_of_edges(),
        connected_components=nx.number_connected_components(graph) if graph.number_of_nodes() > 0 else 0,
        density=nx.density(graph) if graph.number_of_nodes() > 1 else 0.0,
        top_nodes=top_nodes,
        top_edges=top_edges,
    )
    return graph, summary


def export_tables(graph: nx.Graph, nodes_path: Path, edges_path: Path) -> None:
    with nodes_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["institution", "researchers", "weighted_degree"])
        for node in sorted(graph.nodes, key=str.casefold):
            display_name = graph.nodes[node].get("display_name", node)
            writer.writerow(
                [
                    display_name,
                    graph.nodes[node].get("researchers", 0),
                    graph.degree(node, weight="weight"),
                ]
            )

    with edges_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["source", "target", "shared_researchers"])
        for left, right, data in sorted(
            graph.edges(data=True),
            key=lambda row: (int(row[2].get("weight", 0)), row[0].casefold(), row[1].casefold()),
            reverse=True,
        ):
            left_name = graph.nodes[left].get("display_name", left)
            right_name = graph.nodes[right].get("display_name", right)
            writer.writerow([left_name, right_name, int(data.get("weight", 0))])


def export_networkx_graph(graph: nx.Graph, output_gexf: Path) -> None:
        nx.write_gexf(graph, output_gexf)


def to_markdown_table(rows: list[tuple[str, int, int, float]]) -> str:
    lines = [
        "| Institución | Investigadores afiliados | Peso de conexión | Centralidad de grado |",
        "|---|---:|---:|---:|",
    ]
    for institution, researchers, strength, centrality in rows:
        lines.append(
            f"| {institution} | {researchers} | {strength} | {centrality:.4f} |"
        )
    return "\n".join(lines)


def to_edge_table(rows: list[tuple[str, str, int]]) -> str:
    lines = [
        "| Institución A | Institución B | Investigadores compartidos |",
        "|---|---|---:|",
    ]
    for left, right, shared in rows:
        lines.append(f"| {left} | {right} | {shared} |")
    return "\n".join(lines)


def build_markdown(summary: NetworkSummary, min_shared: int) -> str:
    ratio_multi = (
        (summary.investigators_multi_affiliation / summary.investigators_with_affiliation) * 100
        if summary.investigators_with_affiliation
        else 0.0
    )
    return f"""# Sprint 3 - Network analysis de co-filiación

## Objetivo

Construir un grafo institucional de co-filiación usando `INST_FILIA` (separado por `|`), donde:

- Nodos: instituciones.
- Aristas: pares de instituciones conectadas por investigadores compartidos.
- Peso de arista: número de investigadores que comparten ambas instituciones.

## Configuración del modelo

- Fuente: `datos/tarea_join/investigadores_consolidado.csv`
- Umbral mínimo de investigadores compartidos por arista: **{min_shared}**
- Se normalizaron variantes institucionales (sedes, paréntesis y formatos de escritura) para reducir duplicados nominales.

## Métricas generales del grafo

- Investigadores con al menos una afiliación: **{summary.investigators_with_affiliation}**
- Investigadores con co-filiación (>=2 instituciones): **{summary.investigators_multi_affiliation}**
- Porcentaje con co-filiación: **{ratio_multi:.2f}%**
- Instituciones (nodos activos): **{summary.institutions_total}**
- Conexiones de co-filiación (aristas): **{summary.edges_total}**
- Componentes conectados: **{summary.connected_components}**
- Densidad de red: **{summary.density:.6f}**

## Instituciones más conectadas

{to_markdown_table(summary.top_nodes)}

## Pares institucionales con mayor co-filiación

{to_edge_table(summary.top_edges)}

## Entregables

- `hallazgos/sprint_3_cofiliacion_network.md`: reporte del Sprint 3.
- `hallazgos/sprint_3_cofiliacion_nodes.csv`: tabla de nodos.
- `hallazgos/sprint_3_cofiliacion_edges.csv`: tabla de aristas.
- `hallazgos/sprint_3_cofiliacion_network.gexf`: grafo exportado desde NetworkX.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sprint 3 - Red de co-filiación institucional")
    parser.add_argument(
        "--min-shared",
        type=int,
        default=2,
        help="Mínimo de investigadores compartidos para conservar una arista.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    graph, summary = build_network(DATA_PATH, min_shared=max(1, args.min_shared))
    export_tables(graph, OUTPUT_NODES, OUTPUT_EDGES)
    export_networkx_graph(graph, OUTPUT_GEXF)
    OUTPUT_MD.write_text(build_markdown(summary, min_shared=max(1, args.min_shared)), encoding="utf-8")

    print(f"Reporte Markdown generado en: {OUTPUT_MD}")
    print(f"Nodos exportados en: {OUTPUT_NODES}")
    print(f"Aristas exportadas en: {OUTPUT_EDGES}")
    print(f"Grafo NetworkX exportado en: {OUTPUT_GEXF}")


if __name__ == "__main__":
    main()