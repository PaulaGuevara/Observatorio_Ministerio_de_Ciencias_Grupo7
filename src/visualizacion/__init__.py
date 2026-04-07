from .distribuciones import (
    figura_distribucion_categoria,
    figura_distribucion_genero,
    preparar_distribucion_categoria,
    preparar_distribucion_genero,
)
from .instituciones import (
    expandir_instituciones,
    filtrar_instituciones,
    figura_ranking_instituciones,
    obtener_columna_area,
    ranking_instituciones,
)
from .mapas import figura_mapa_departamentos, tabla_top_departamentos

__all__ = [
    "expandir_instituciones",
    "figura_distribucion_categoria",
    "figura_distribucion_genero",
    "figura_mapa_departamentos",
    "figura_ranking_instituciones",
    "filtrar_instituciones",
    "obtener_columna_area",
    "preparar_distribucion_categoria",
    "preparar_distribucion_genero",
    "ranking_instituciones",
    "tabla_top_departamentos",
]