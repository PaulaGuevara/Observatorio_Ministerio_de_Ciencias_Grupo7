# Hallazgos — Inventario de notebooks_Minciencias

Este documento resume qué contiene cada carpeta y archivo de `notebooks_Minciencias`, para facilitar navegación, presentación y trazabilidad del trabajo.

## Estructura general

- `notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/`
- `notebooks_Minciencias/tarea_dimensiones_y_hechos_Minciencias/`
- `notebooks_Minciencias/tarea_gran_tabla_Minciencias/`
- `notebooks_Minciencias/tarea_join_Minciencias/`
- `notebooks_Minciencias/tarea_tabla_Minciencias/`

---

## 1) tarea_anlisis_bases_de_datos_Minciencias

### Archivos
- `2019_analisis.md`  
  Informe descriptivo de la convocatoria 2019: faltantes, perfil demográfico, distribución geográfica, gran área y cruce género × área.

- `2019_codigo.py`  
  Script en Python para generar análisis y gráficas de la base 2019 (faltantes, barras, cruces y distribuciones).

- `analisis_17.md`  
  Informe exploratorio de la convocatoria 2017 con interpretación de faltantes, variables clave, distribución por género, edad, área y territorio.

- `datos_2021.ipynb`  
  Notebook de análisis 2021 (filtro por año, faltantes, duplicados, género, edad, región y formación).

- `inv_17_codigo_graficas.R`  
  Script en R para construir visualizaciones detalladas del análisis 2017.

### Subcarpeta
- `graficos_2019/`
  - `faltantes.png`: visualización de porcentaje de datos faltantes.
  - `genero.png`: distribución por género.
  - `gran_area.png`: distribución por gran área del conocimiento.
  - `gran_area_gener.png`: cruce gran área × género.

---

## 2) tarea_dimensiones_y_hechos_Minciencias

### Archivos
- `README.md`  
  Documenta la creación de dimensiones (investigador, convocatoria, nacimiento, universidad, nivel de formación, residencia) y su exportación.

- `codigo_dimensiones_C.R`  
  Script en R para construir tablas de dimensiones desde la base consolidada.

- `tabla_hechos_codigo.R`  
  Script en R para crear la tabla de hechos uniendo dimensiones relevantes.

- `dimensiones.ipynb`  
  Notebook de apoyo para exploración y/o validación de las dimensiones.

---

## 3) tarea_gran_tabla_Minciencias

### Archivos de análisis y reporte
- `analisis_Univariado.md`  
  Informe univariado sobre la gran tabla (numéricas, categóricas, temporal, tablas de frecuencias y porcentajes).

- `informe_multivariado.md`  
  Informe multivariado (correspondencias simples/múltiples y análisis factorial mixto).

- `informe_clusters.md`  
  Informe técnico de clústeres con K-Prototypes y perfiles resultantes.

### Archivos de código
- `codigo_analisis_univariado.py`  
  Script Python del análisis univariado sobre la gran tabla.

- `codigo_creacion_gran_tabla_a_partir_del_modelo_estrella.py`  
  Script Python para construir la gran tabla desde modelo estrella y generar reporte de uniones.

- `analisis_multivariado_base_gran_table.R`  
  Script R para análisis multivariado (CA, MCA, FAMD y visualización asociada).

- `analisis_de_clusters.R`  
  Script R para clustering con variables mixtas (K-Prototypes).

### Notebooks
- `analisis2.ipynb` y `analisis2_(1).ipynb`  
  Versiones de notebook usadas para pruebas o iteraciones de análisis en gran tabla.

---

## 4) tarea_join_Minciencias

### Archivo
- `codigo_join.py`  
  Script en Python para unir bases de convocatorias (2017, 2019, 2021) y exportar consolidado en CSV/Excel.

---

## 5) tarea_tabla_Minciencias

### Archivos
- `README.md`  
  Describe la depuración de IDs duplicados por convocatoria y el criterio de conservar el registro más reciente por persona.

- `arreglar_base_consultoria_7.R`  
  Script R para depuración de duplicados y validaciones de unicidad/coherencia de IDs.

---

## 6) entregables_hallazgos

### Archivos
- `sprint_2_hhi_concentracion_territorial.md`  
  Informe del Sprint 2 con cálculo del índice Herfindahl-Hirschman por departamento de residencia, interpretación metodológica y respuesta puntual sobre la concentración en Bogotá, Antioquia y Valle del Cauca.

- `sprint_2_hhi_concentracion_territorial.html`  
  Versión visual del mismo análisis, lista para mostrar en navegador o en clase.

- `sprint_3_cofiliacion_network.md`  
  Informe del Sprint 3 con análisis de red de co-filiación institucional usando `INST_FILIA`, métricas principales de red, top de instituciones más conectadas y pares con mayor número de investigadores compartidos.

- `sprint_3_cofiliacion_nodes.csv`  
  Tabla de nodos del grafo (institución, investigadores afiliados y peso total de conexiones).

- `sprint_3_cofiliacion_edges.csv`  
  Tabla de aristas del grafo (institución origen, institución destino e investigadores compartidos).

- `sprint_3_cofiliacion_network.gexf`  
  Exportación del grafo en formato GEXF generado con NetworkX para análisis de red en herramientas compatibles.

- `sprint_3_cofiliacion_grafo_interactivo.html`  
  Visualización HTML interactiva del grafo de co-filiación usando Pyvis. Incluye physics engine Barnes-Hut, tooltips informativos, navegación con mouse (arrastrar, zoom, pan) y controles de física integrados. **Abre directamente en navegador sin dependencias externas.**

- `dashboard_sprint_3.py`  
  Dashboard Streamlit del Sprint 3 #18 con visualización interactiva del grafo de co-filiación usando Pyvis (filtros de umbral de aristas y tamaño de red).

- `dashboard_observatorio.py`  
  Dashboard Streamlit unificado con dos pestañas: Sprint 2 (análisis HHI + mapa territorial de concentración de investigadores) y Sprint 3 (grafo interactivo de co-filiación institucional).

