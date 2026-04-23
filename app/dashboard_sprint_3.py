from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"


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


@st.cache_data(show_spinner=False)
def build_graph(min_shared: int) -> tuple[nx.Graph, dict[str, int]]:
    node_people: Counter[str] = Counter()
    edge_people: Counter[tuple[str, str]] = Counter()
    display_name_by_canonical: dict[str, Counter[str]] = {}

    meta = {
        "people_with_aff": 0,
        "people_multi_aff": 0,
    }

    with DATA_PATH.open("r", encoding="latin-1", newline="") as file_obj:
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

            meta["people_with_aff"] += 1
            for institution in canonical_affiliations:
                node_people[institution] += 1

            if len(canonical_affiliations) < 2:
                continue

            meta["people_multi_aff"] += 1
            for left, right in combinations(sorted(canonical_affiliations, key=str.casefold), 2):
                edge_people[(left, right)] += 1

    graph = nx.Graph()
    for institution, people in node_people.items():
        display_counter = display_name_by_canonical.get(institution, Counter())
        display_name = display_counter.most_common(1)[0][0] if display_counter else institution
        graph.add_node(institution, researchers=people, display_name=display_name)

    for (left, right), shared in edge_people.items():
        if shared >= min_shared:
            graph.add_edge(left, right, weight=shared)

    graph.remove_nodes_from([node for node in graph.nodes if graph.degree(node) == 0])
    return graph, meta


def build_pyvis_html(graph: nx.Graph, max_nodes: int) -> str:
    if graph.number_of_nodes() > max_nodes:
        top_nodes = sorted(
            graph.nodes,
            key=lambda node: (
                graph.degree(node, weight="weight"),
                graph.nodes[node].get("researchers", 0),
            ),
            reverse=True,
        )[:max_nodes]
        graph = graph.subgraph(top_nodes).copy()

    net = Network(height="760px", width="100%", bgcolor="#f7f4ef", font_color="#1f2937", notebook=False)
    net.barnes_hut(gravity=-22000, central_gravity=0.24, spring_length=160, spring_strength=0.02)

    for node in graph.nodes:
        label = str(graph.nodes[node].get("display_name", node))
        researchers = int(graph.nodes[node].get("researchers", 0))
        strength = int(graph.degree(node, weight="weight"))
        size = 10 + min(44, researchers**0.5)
        net.add_node(
            node,
            label=label,
            size=size,
            color="#0f766e",
            title=(
                f"Institución: {label}<br>"
                f"Investigadores afiliados: {researchers}<br>"
                f"Peso total de conexiones: {strength}"
            ),
        )

    for left, right, data in graph.edges(data=True):
        shared = int(data.get("weight", 0))
        net.add_edge(
            left,
            right,
            value=shared,
            width=1 + min(10, shared / 2),
            color="#b45309",
            title=f"Investigadores compartidos: {shared}",
        )

    net.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "font": {"size": 16, "face": "Georgia"}
          },
          "edges": {
            "smooth": {"enabled": true, "type": "dynamic"}
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "tooltipDelay": 90
          },
          "physics": {
            "enabled": true,
            "stabilization": {"enabled": true, "iterations": 220}
          }
        }
        """
    )
    return net.generate_html(name="Co-filiación institucional")


def top_institutions(graph: nx.Graph, n: int = 15) -> list[dict[str, float | int | str]]:
    centrality = nx.degree_centrality(graph) if graph.number_of_nodes() > 1 else {}
    rows = []
    for node in graph.nodes:
        rows.append(
            {
                "institucion": str(graph.nodes[node].get("display_name", node)),
                "investigadores_afiliados": int(graph.nodes[node].get("researchers", 0)),
                "peso_conexiones": int(graph.degree(node, weight="weight")),
                "centralidad_grado": float(centrality.get(node, 0.0)),
            }
        )
    rows.sort(
        key=lambda row: (
            int(row["peso_conexiones"]),
            int(row["investigadores_afiliados"]),
            str(row["institucion"]).casefold(),
        ),
        reverse=True,
    )
    return rows[:n]


def main() -> None:
    st.set_page_config(page_title="Sprint 3 - Co-filiación", page_icon="🕸️", layout="wide")
    st.title("Sprint 3 #18 - Visualización interactiva de co-filiación")
    st.caption("Grafo institucional construido desde INST_FILIA con NetworkX y renderizado con Pyvis")

    with st.sidebar:
        st.header("Parámetros")
        min_shared = st.slider("Mínimo de investigadores por arista", min_value=1, max_value=15, value=2)
        max_nodes = st.slider("Máximo de nodos en pantalla", min_value=30, max_value=500, value=160, step=10)

    graph, meta = build_graph(min_shared=min_shared)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Investigadores con afiliación", f"{meta['people_with_aff']:,}".replace(",", "."))
    c2.metric("Investigadores con co-filiación", f"{meta['people_multi_aff']:,}".replace(",", "."))
    c3.metric("Instituciones (nodos)", graph.number_of_nodes())
    c4.metric("Conexiones (aristas)", graph.number_of_edges())

    density = nx.density(graph) if graph.number_of_nodes() > 1 else 0.0
    st.write(f"Densidad de red: **{density:.6f}**")

    if graph.number_of_nodes() == 0:
        st.warning("No hay nodos para visualizar con los filtros actuales.")
        return

    html = build_pyvis_html(graph, max_nodes=max_nodes)
    components.html(html, height=790, scrolling=True)

    st.subheader("Top instituciones más conectadas")
    st.dataframe(top_institutions(graph), use_container_width=True)


if __name__ == "__main__":
    main()