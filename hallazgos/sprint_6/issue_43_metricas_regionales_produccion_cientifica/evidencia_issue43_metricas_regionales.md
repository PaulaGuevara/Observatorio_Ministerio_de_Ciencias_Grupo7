# Evidencia Issue #43: Construcción de métricas regionales de producción científica

## Sprint 6

**Issue:** #43  
**Nombre de la tarea:** Construcción de métricas regionales de producción científica  
**Tipo de tarea:** Cálculo de indicadores, generación de resultados y documentación técnica  
**Responsable:** Maria Paula Amaya  

---

## 1. Objetivo de la tarea

El objetivo de esta tarea fue calcular indicadores regionales de producción científica a partir de la base consolidada del proyecto y generar una evidencia técnica que permitiera consultar las fórmulas, los resultados y las visualizaciones asociadas.

La tarea se desarrolló tomando como base la propuesta metodológica del proyecto, en la cual se definieron indicadores orientados a analizar la distribución territorial de la producción científica registrada en Minciencias.

---

## 2. Fuente de información utilizada

Los cálculos se realizaron a partir de la base consolidada en formato Parquet, construida previamente mediante la integración de productos científicos, investigadores reconocidos y grupos de investigación.

Archivo base utilizado:

- datos/processed/consolidado_produccion_investigadores_match.parquet

La unidad principal de análisis es el producto científico asociado a un grupo de investigación.

---

## 3. Criterio territorial del análisis

El análisis territorial se realizó usando como eje principal la ubicación del grupo de investigación.

Variable principal utilizada:

- NME_REGION_GR

Esta decisión metodológica permite asociar cada producto científico al territorio del grupo de investigación, manteniendo coherencia con la estructura de la base consolidada.

La información territorial del investigador se considera complementaria y solo se utiliza cuando existe un cruce válido entre productos e investigadores.

---

## 4. Indicadores calculados

En esta tarea se calcularon los 16 indicadores regionales considerados dentro de la propuesta del proyecto.

| No. | Indicador |
|---:|---|
| 1 | Producción total por región |
| 2 | Participación porcentual regional |
| 3 | Producción promedio por grupo |
| 4 | Producción por clasificación del grupo |
| 5 | Diversidad de producción científica |
| 6 | Índice de especialización productiva |
| 7 | Diversidad relativa regional |
| 8 | Permanencia de grupos por región |
| 9 | Crecimiento de grupos por región |
| 10 | Consolidación de grupos por región |
| 11 | Renovación de grupos por región |
| 12 | Distribución de registros por género y región |
| 13 | Evolución detallada de grupos |
| 14 | Evolución de grupos por región |
| 15 | Participación por clasificación del grupo |
| 16 | Participación por clasificación, región y convocatoria |

Estos indicadores permiten analizar volumen, participación, productividad media, clasificación, diversidad, especialización, permanencia, crecimiento, consolidación, renovación y evolución regional.

---

## 5. Scripts desarrollados

Para el desarrollo del issue se organizaron los scripts dentro de la carpeta correspondiente al issue #43.

Archivos de código asociados:

- src/issue_43/calcular_indicadores_regionales.py
- src/issue_43/generar_html_issue43.py

El primer script calcula los indicadores regionales y exporta los resultados en archivos CSV.

El segundo script genera un reporte HTML interactivo, con diseño visual mejorado, fórmulas, tablas y gráficas para facilitar la consulta de los resultados.

---

## 6. Archivos de salida generados

Los indicadores calculados se exportaron en archivos CSV dentro de la carpeta de resultados del proyecto.

Carpeta de salida:

- outputs/indicadores/

Entre los archivos generados se encuentran:

- 01_produccion_total_region_match.csv
- 02_participacion_region_match.csv
- 03_promedio_por_grupo_match.csv
- 04_produccion_clasificacion_region_match.csv
- 05_diversidad_region_match.csv
- 06_indice_especializacion_productiva_match.csv
- 07_diversidad_relativa_region_match.csv
- 08_permanencia_grupos_region_match.csv
- 09_crecimiento_grupos_region_match.csv
- 10_consolidacion_grupos_region_match.csv
- 11_renovacion_grupos_region_match.csv
- 12_genero_region_match.csv
- 13_evolucion_grupos_detalle_match.csv
- 14_evolucion_grupos_region_match.csv
- 15_participacion_clasificacion_region_match.csv
- 16_participacion_clasificacion_region_convocatoria_match.csv

---

## 7. Reporte HTML generado

Además de los archivos CSV, se generó un reporte HTML para consultar los indicadores de forma visual.

Archivo HTML asociado:

- docs/issue_43/indicadores_issue43.html

Este reporte incluye:

- Nota metodológica.
- KPIs generales.
- Navegación por indicador.
- Fórmulas utilizadas.
- Descripción de cada indicador.
- Interpretación técnica.
- Gráficas interactivas.
- Tablas con resultados.

---

## 8. Relación con la pregunta del proyecto

Los indicadores calculados aportan evidencia para responder la pregunta central del proyecto:

> ¿Cómo se distribuye regionalmente la producción científica registrada en Minciencias en las convocatorias 2017, 2019 y 2021?

El cálculo de estas métricas permite observar no solo qué regiones concentran mayor producción científica, sino también cómo se comportan en términos de participación, diversidad, permanencia, crecimiento y consolidación de grupos.

---

## 9. Resultado de la tarea

La tarea se considera desarrollada porque:

- Se calcularon los 16 indicadores regionales definidos en la propuesta.
- Se generaron archivos CSV con los resultados de cada indicador.
- Se creó un reporte HTML interactivo para consultar fórmulas, gráficas y tablas.
- Se organizaron los scripts asociados al issue #43 dentro de src/issue_43.
- Se dejó evidencia documental del desarrollo realizado en el Sprint 6.

---

## 10. Archivos relacionados

- src/issue_43/calcular_indicadores_regionales.py
- src/issue_43/generar_html_issue43.py
- docs/issue_43/indicadores_issue43.html
- outputs/indicadores/
- hallazgos/sprint_6/issue_43_metricas_regionales_produccion_cientifica/evidencia_issue43_metricas_regionales.md

---

## 11. Conclusión

El Issue #43 permitió construir métricas regionales de producción científica de manera reproducible, a partir de la base consolidada del proyecto.

Los resultados generados fortalecen el análisis territorial del proyecto, ya que permiten comparar regiones desde diferentes perspectivas: volumen, participación, productividad, diversidad, clasificación, permanencia, crecimiento y consolidación.

