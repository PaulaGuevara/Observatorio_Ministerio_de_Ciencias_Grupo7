"""
Construccion del grafo de co-filiacion institucional — Sprint 3

Construye un grafo bipartito investigador–institucion y lo proyecta
en un grafo institucion–institucion donde el peso del arco es el numero
de investigadores que comparten ambas instituciones en una misma convocatoria.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------

def cargar_datos(anio: int | None = None) -> pd.DataFrame:
    """Carga el consolidado y filtra opcionalmente por año de convocatoria."""
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df["ANO_CONVO"] = pd.to_datetime(df["ANO_CONVO"], dayfirst=True, errors="coerce").dt.year
    df = df.dropna(subset=["INST_FILIA", "ID_PERSONA_PR"])
    df["INST_FILIA"] = df["INST_FILIA"].str.strip().str.upper()
    if anio is not None:
        df = df[df["ANO_CONVO"] == anio]
    return df


# ---------------------------------------------------------------------------
# Construccion del grafo
# ---------------------------------------------------------------------------

def construir_grafo_cofiliacion(
    df: pd.DataFrame,
    top_n: int | None = 50,
) -> nx.Graph:
    """
    Construye un grafo de co-filiacion institucional.

    Dos instituciones estan conectadas si al menos un investigador
    aparece en ambas en distintas convocatorias, o si se decide
    usar la co-publicacion por area de conocimiento.

    En este caso usamos: dos instituciones comparten un arco si al menos
    un investigador (ID_PERSONA_PR) figura en ambas a lo largo del tiempo.

    Parameters
    ----------
    df : DataFrame con columnas ID_PERSONA_PR, INST_FILIA, ANO_CONVO
    top_n : limitar a las N instituciones con mas investigadores (None = todas)

    Returns
    -------
    G : grafo no dirigido ponderado (peso = investigadores compartidos)
    """
    # Filtrar instituciones con mas presencia si se pide top_n
    if top_n is not None:
        top_inst = (
            df["INST_FILIA"]
            .value_counts()
            .head(top_n)
            .index
        )
        df = df[df["INST_FILIA"].isin(top_inst)]

    # Para cada investigador, obtener todas sus instituciones a lo largo del tiempo
    inv_inst = (
        df.groupby("ID_PERSONA_PR")["INST_FILIA"]
        .apply(lambda x: sorted(set(x)))
        .reset_index()
    )
    inv_inst = inv_inst[inv_inst["INST_FILIA"].map(len) > 1]

    G = nx.Graph()

    # Agregar nodos con atributos
    conteo_inst = df["INST_FILIA"].value_counts()
    for inst, n in conteo_inst.items():
        G.add_node(inst, n_investigadores=int(n))

    # Agregar arcos: co-aparicion del mismo investigador en varias instituciones
    for _, row in inv_inst.iterrows():
        instituciones = row["INST_FILIA"]
        for i in range(len(instituciones)):
            for j in range(i + 1, len(instituciones)):
                u, v = instituciones[i], instituciones[j]
                if G.has_edge(u, v):
                    G[u][v]["weight"] += 1
                else:
                    G.add_edge(u, v, weight=1)

    return G


def construir_grafo_area(
    df: pd.DataFrame,
    top_n: int | None = 40,
) -> nx.Graph:
    """
    Grafo de co-ocurrencia entre instituciones dentro de la misma gran area OCDE.

    Dos instituciones estan conectadas si tienen investigadores en la misma
    gran area del conocimiento. Peso = numero de investigadores compartidos por area.
    """
    df = df.dropna(subset=["NME_GRAN_AREA_PR"])
    if top_n is not None:
        top_inst = df["INST_FILIA"].value_counts().head(top_n).index
        df = df[df["INST_FILIA"].isin(top_inst)]

    G = nx.Graph()

    conteo_inst = df["INST_FILIA"].value_counts()
    for inst, n in conteo_inst.items():
        G.add_node(inst, n_investigadores=int(n))

    for area, grupo in df.groupby("NME_GRAN_AREA_PR"):
        instituciones = grupo["INST_FILIA"].unique().tolist()
        for i in range(len(instituciones)):
            for j in range(i + 1, len(instituciones)):
                u, v = instituciones[i], instituciones[j]
                if G.has_edge(u, v):
                    G[u][v]["weight"] += grupo[grupo["INST_FILIA"].isin([u, v])]["ID_PERSONA_PR"].nunique()
                else:
                    G.add_edge(u, v, weight=1, areas=[area])

    return G


# ---------------------------------------------------------------------------
# Metricas de red
# ---------------------------------------------------------------------------

def calcular_metricas(G: nx.Graph) -> dict:
    """Calcula metricas globales y por nodo del grafo."""
    if G.number_of_nodes() == 0:
        return {}

    metricas = {
        "n_nodos": G.number_of_nodes(),
        "n_arcos": G.number_of_edges(),
        "densidad": round(nx.density(G), 4),
        "componentes_conectados": nx.number_connected_components(G),
    }

    # Componente gigante
    componentes = sorted(nx.connected_components(G), key=len, reverse=True)
    if componentes:
        gc = G.subgraph(componentes[0])
        metricas["nodos_componente_gigante"] = gc.number_of_nodes()
        if gc.number_of_nodes() > 1:
            metricas["diametro"] = nx.diameter(gc)
            metricas["clustering_medio"] = round(nx.average_clustering(gc), 4)

    # Centralidades por nodo
    degree_centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]

    metricas["top_degree"] = [(n, round(v, 4)) for n, v in top_degree]
    metricas["top_betweenness"] = [(n, round(v, 4)) for n, v in top_betweenness]

    # Deteccion de comunidades (Louvain via greedy modularity)
    comunidades = list(nx.community.greedy_modularity_communities(G, weight="weight"))
    metricas["n_comunidades"] = len(comunidades)
    metricas["comunidades"] = [sorted(c) for c in comunidades]

    return metricas


def tabla_nodos(G: nx.Graph) -> pd.DataFrame:
    """DataFrame con atributos y centralidades de cada nodo."""
    degree_centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    filas = []
    for nodo, datos in G.nodes(data=True):
        filas.append({
            "institucion": nodo,
            "n_investigadores": datos.get("n_investigadores", 0),
            "grado": G.degree(nodo),
            "degree_centrality": round(degree_centrality.get(nodo, 0), 4),
            "betweenness_centrality": round(betweenness.get(nodo, 0), 4),
        })

    return pd.DataFrame(filas).sort_values("grado", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Punto de entrada para pruebas
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = cargar_datos()
    print(f"Registros cargados: {len(df):,}")

    G = construir_grafo_cofiliacion(df, top_n=50)
    print(f"\nGrafo de co-filiacion:")
    print(f"  Nodos: {G.number_of_nodes()}")
    print(f"  Arcos: {G.number_of_edges()}")

    metricas = calcular_metricas(G)
    print(f"  Densidad: {metricas.get('densidad')}")
    print(f"  Componentes: {metricas.get('componentes_conectados')}")
    print(f"  Comunidades: {metricas.get('n_comunidades')}")
    print("\n  Top 5 por degree centrality:")
    for nodo, v in metricas.get("top_degree", [])[:5]:
        print(f"    {nodo}: {v}")
