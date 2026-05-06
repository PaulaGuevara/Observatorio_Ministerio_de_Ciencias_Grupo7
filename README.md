# Observatorio MinCiencias — Investigadores Reconocidos

> Ustadistica - Consultoria e Investigacion - Universidad Santo Tomas - 2026-I

Repositorio del proyecto de consultoria para analizar convocatorias de investigadores reconocidos por MinCiencias (2017, 2019, 2021), con enfoque longitudinal, territorial y de co-filiacion.

## Objetivo

Construir evidencia analitica reproducible y visualmente interpretable para responder preguntas de retencion, transicion de categorias, concentracion territorial y estructura de redes de co-filiacion institucional.

## Navegacion Rapida (para validacion)

- Reporte visual comparativo: [hallazgos/reporte_visual_comparativo.html](hallazgos/reporte_visual_comparativo.html)
- Informe final Sprint 4 (Markdown): [docs/sprint_4_informe_final.md](docs/sprint_4_informe_final.md)
- Informe final Sprint 4 (HTML): [hallazgos/sprint_4_informe_final.html](hallazgos/sprint_4_informe_final.html)
- Evidencias de tareas y matrices: [hallazgos/evidencias/](hallazgos/evidencias)
- Guia de organizacion del repositorio: [docs/organizacion_repositorio.md](docs/organizacion_repositorio.md)

## Estructura Real del Repositorio

```text
Observatorio_Ministerio_de_Ciencias_Grupo7/
|- README.md
|- CONTRIBUTING.md
|- pyproject.toml
|- Dockerfile
|- app/
|  |- streamlit_app.py
|  |- dashboard_observatorio.py
|  |- dashboard_sprint_3.py
|  |- legacy/
|     |- streamlit_app_legacy.py
|- artifacts/
|  |- sprint2_genero_ocde/
|- datos/
|  |- catalogo.yaml
|  |- raw/
|  |- processed/
|  |- tarea_join/
|     |- investigadores_consolidado.csv
|- diccionario/
|  |- diccionario_minciencias.yaml
|- docs/
|  |- sprint_4_informe_final.md
|- hallazgos/
|  |- README.md
|  |- evidencias/
|  |- reporte_visual_comparativo.html
|  |- sprint_2_hhi_concentracion_territorial.md
|  |- sprint_2_hhi_concentracion_territorial.html
|  |- sprint_3_cofiliacion_network.md
|  |- sprint_3_cofiliacion_grafo_interactivo.html
|  |- sprint_4_informe_final.html
|- notebooks/
|- notebooks_Minciencias/
|- src/
|  |- ingesta.py
|  |- Transformacion.py
|  |- ingesta/
|  |- transformacion/
|  |- modelo/
|  |- visualizacion/
|- tests/
|- informe_final.md
|- MARCO_TEORICO.md
|- catalogo.yaml
```

## Convenciones de Orden (Marie Kondo)

- `datos/`: fuentes y productos de datos.
- `notebooks/` y `notebooks_Minciencias/`: trabajo exploratorio y desarrollo historico.
- `hallazgos/`: salidas finales para socializacion (HTML, MD, CSV, GEXF) y evidencias.
- `src/`: codigo reusable por modulos.
- `app/`: dashboards y aplicaciones Streamlit.
- `docs/`: documentacion formal de entrega.

No se eliminan archivos historicos; se privilegia claridad por ubicacion, nombre e indice.

## Ejecucion Basica

```bash
pip install poetry
poetry install

# Dashboard principal (si aplica en tu entorno)
poetry run streamlit run app/streamlit_app.py
```

## Metodologia

- Framework analitico: CRISP-DM
- Gestion: Sprints y Git Flow (`main`, `develop`, `feature/*`)
- Control de calidad: revisiones por pares y trazabilidad por evidencias

Consultar [CONTRIBUTING.md](CONTRIBUTING.md) para flujo de contribucion.
