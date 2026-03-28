"""
Visualizacion interactiva del grafo de redes institucionales — Sprint 3

Genera grafos HTML con Pyvis a partir de grafos NetworkX.
Incluye estilos visuales segun comunidad y centralidad del nodo.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import networkx as nx
from pyvis.network import Network

# Paleta de colores para comunidades (hasta 10)
COLORES_COMUNIDADES = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#e91e63", "#00bcd4",
]


def _asignar_comunidades(G: nx.Graph) -> dict[str, int]:
    """Detecta comunidades con greedy modularity y retorna {nodo: id_comunidad}."""
    comunidades = list(nx.community.greedy_modularity_communities(G, weight="weight"))
    mapa = {}
    for idx, comunidad in enumerate(comunidades):
        for nodo in comunidad:
            mapa[nodo] = idx
    return mapa


def grafo_a_html(
    G: nx.Graph,
    titulo: str = "Red de co-filiacion institucional",
    altura: str = "600px",
    fisica: bool = True,
) -> str:
    """
    Convierte un grafo NetworkX a HTML interactivo con Pyvis.

    El tamanio de cada nodo es proporcional a su numero de investigadores.
    El color indica la comunidad detectada por Louvain/greedy modularity.
    El grosor de los arcos es proporcional al peso (investigadores compartidos).

    Parameters
    ----------
    G      : grafo NetworkX (no dirigido, ponderado)
    titulo : titulo que aparece en el HTML
    altura : altura del canvas
    fisica : activar simulacion de fuerzas interactiva

    Returns
    -------
    html_str : string con el HTML completo para renderizar
    """
    if G.number_of_nodes() == 0:
        return "<p>El grafo no tiene nodos para mostrar.</p>"

    net = Network(
        height=altura,
        width="100%",
        bgcolor="#f8f9fa",
        font_color="#333333",
        heading=titulo,
    )

    comunidades = _asignar_comunidades(G)
    degree_centrality = nx.degree_centrality(G)
    max_inv = max((d.get("n_investigadores", 1) for _, d in G.nodes(data=True)), default=1)

    for nodo, datos in G.nodes(data=True):
        n_inv = datos.get("n_investigadores", 1)
        grado = G.degree(nodo)
        comunidad_id = comunidades.get(nodo, 0)
        color = COLORES_COMUNIDADES[comunidad_id % len(COLORES_COMUNIDADES)]

        # Tamanio: escalar entre 10 y 50 segun n_investigadores
        tamano = 10 + (n_inv / max_inv) * 40

        # Etiqueta con nombre truncado
        etiqueta = nodo[:45] + "..." if len(nodo) > 45 else nodo

        titulo_hover = (
            f"<b>{nodo}</b><br>"
            f"Investigadores: {n_inv:,}<br>"
            f"Conexiones: {grado}<br>"
            f"Centralidad: {degree_centrality.get(nodo, 0):.3f}<br>"
            f"Comunidad: {comunidad_id + 1}"
        )

        net.add_node(
            nodo,
            label=etiqueta,
            title=titulo_hover,
            size=tamano,
            color=color,
            borderWidth=2,
            borderWidthSelected=4,
            font={"size": 11},
        )

    # Normalizar pesos de arcos para el grosor visual
    pesos = [d.get("weight", 1) for _, _, d in G.edges(data=True)]
    max_peso = max(pesos) if pesos else 1

    for u, v, datos in G.edges(data=True):
        peso = datos.get("weight", 1)
        grosor = 1 + (peso / max_peso) * 8

        net.add_edge(
            u, v,
            value=grosor,
            title=f"Investigadores compartidos: {peso}",
            color={"color": "#aaaaaa", "highlight": "#555555"},
        )

    # Opciones de visualizacion
    opciones = """
    {
      "nodes": {
        "shape": "dot",
        "shadow": {"enabled": true, "size": 5}
      },
      "edges": {
        "smooth": {"type": "continuous"},
        "shadow": false
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100,
        "navigationButtons": true,
        "keyboard": {"enabled": true}
      },
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "centralGravity": 0.01,
          "springLength": 120,
          "springConstant": 0.08
        },
        "solver": "forceAtlas2Based",
        "stabilization": {"iterations": 150}
      }
    }
    """
    net.set_options(opciones)

    if not fisica:
        net.toggle_physics(False)

    # Guardar a archivo temporal y leer el HTML
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        tmp_path = f.name

    net.save_graph(tmp_path)
    html = Path(tmp_path).read_text(encoding="utf-8")
    Path(tmp_path).unlink(missing_ok=True)

    return html


def grafo_a_html_filtrado(
    G: nx.Graph,
    comunidad: int | None = None,
    min_grado: int = 1,
    altura: str = "600px",
) -> str:
    """
    Renderiza el grafo aplicando filtros de comunidad y grado minimo.

    Parameters
    ----------
    G          : grafo completo
    comunidad  : ID de comunidad a mostrar (None = todas)
    min_grado  : grado minimo para mostrar un nodo
    altura     : altura del canvas
    """
    G_filtrado = G.copy()

    # Filtrar por grado minimo
    nodos_bajos = [n for n, d in G_filtrado.degree() if d < min_grado]
    G_filtrado.remove_nodes_from(nodos_bajos)

    # Filtrar por comunidad
    if comunidad is not None:
        mapa_comunidades = _asignar_comunidades(G_filtrado)
        nodos_excluidos = [n for n, c in mapa_comunidades.items() if c != comunidad]
        G_filtrado.remove_nodes_from(nodos_excluidos)

    return grafo_a_html(G_filtrado, altura=altura)
