# Inventario de Notebooks y Scripts del Repositorio

**Sprint 1 — Revisión de archivos existentes**

Este documento cataloga todos los notebooks y scripts disponibles en la carpeta `notebooks/`, evalúa su estado y determina cuáles son **reutilizables** en sprints futuros y cuáles deben **descartarse**.

---

## Resumen ejecutivo

| Categoría | Cantidad de archivos |
|---|---|
| ✅ Reutilizable | 13 |
| 🗑️ Descartar | 5 |
| 📄 Documentación / Informe (no ejecutable) | 7 |

---

## 1. `tarea_join/`

Carpeta que contiene el script de consolidación de las tres bases de datos anuales.

| Archivo | Tipo | Clasificación | Descripción |
|---|---|---|---|
| `codigo_join.py` | Python (.py) | ✅ **Reutilizable** | Une los tres archivos CSV (2017, 2019, 2021) usando `pd.concat` y exporta el resultado a Excel y CSV. Es el primer paso del pipeline de datos. |

**Notas de reutilización:**
- Adaptar las rutas de entrada (`/content/...`) a la ubicación real de los archivos antes de ejecutar.
- Las bases exportadas (`Investigadores_Consolidado.xlsx` / `.csv`) son la entrada para todos los scripts posteriores.

---

## 2. `tarea_tabla/`

Carpeta con el script de depuración y validación de IDs duplicados en la base consolidada.

| Archivo | Tipo | Clasificación | Descripción |
|---|---|---|---|
| `arreglar_base_consultoria_7.R` | R (.R) | ✅ **Reutilizable** | Detecta investigadores presentes en más de una convocatoria y conserva únicamente el registro de la convocatoria más reciente. Valida la unicidad de `ID_PERSONA_PR`. Genera la base limpia de **26.662 registros**. |
| `README.md` | Markdown | 📄 **Documentación** | Describe la lógica de depuración y el resultado del proceso. Útil como referencia. |

**Notas de reutilización:**
- Actualizar la ruta de entrada a `Investigadores_Consolidado.xlsx`.
- La base resultante (`Base_sin_duplicados`) es la entrada del modelo estrella.

---

## 3. `tarea_anlisis_bases_de_datos/`

Carpeta con el análisis exploratorio individual de cada convocatoria (2017, 2019, 2021).

| Archivo | Tipo | Clasificación | Descripción |
|---|---|---|---|
| `inv_17_codigo_graficas.R` | R (.R) | ✅ **Reutilizable** | Análisis exploratorio completo de la base 2017: faltantes, frecuencias y gráficas para todas las variables. Cubre las 30 columnas del dataset. |
| `2019_codigo.py` | Python (.py) | ✅ **Reutilizable** | Análisis exploratorio de la base 2019: faltantes, distribuciones de género, región, área de conocimiento y cruce género × gran área. Bien estructurado y parametrizado. |
| `datos_2021.ipynb` | Jupyter (.ipynb) | ✅ **Reutilizable** | Notebook de análisis exploratorio de la base 2021 (32 celdas): dimensiones, faltantes, distribuciones de género, departamento, clasificación, formación, edad y más. Incluye celdas Markdown con interpretaciones. |
| `2019_analisis.md` | Markdown | 📄 **Documentación** | Informe narrativo de los resultados del análisis exploratorio 2019 con imágenes incrustadas. Sirve como referencia de resultados. |
| `analisis_17.md` | Markdown | 📄 **Documentación** | Informe narrativo del análisis exploratorio 2017. Documenta interpretaciones de cada variable e identifica variables no útiles para visualización. |
| `graficos_2019/faltantes.png` | Imagen PNG | 🗑️ **Descartar** | Salida estática regenerable desde `2019_codigo.py`. |
| `graficos_2019/genero.png` | Imagen PNG | 🗑️ **Descartar** | Salida estática regenerable desde `2019_codigo.py`. |
| `graficos_2019/gran_area.png` | Imagen PNG | 🗑️ **Descartar** | Salida estática regenerable desde `2019_codigo.py`. |
| `graficos_2019/gran_area_gener.png` | Imagen PNG | 🗑️ **Descartar** | Salida estática regenerable desde `2019_codigo.py`. |

**Notas de reutilización:**
- Los tres scripts cubren los mismos tipos de análisis pero por año; se pueden unificar en un único script parametrizado por año en sprints futuros.
- Las imágenes PNG de `graficos_2019/` son outputs estáticos ya referenciados en el informe `.md`. Al poder regenerarse desde el código fuente, no es necesario versionar las imágenes en el repositorio.

---

## 4. `tarea_dimensiones_y_hechos/`

Carpeta con los scripts del modelo estrella (dimensiones + tabla de hechos).

| Archivo | Tipo | Clasificación | Descripción |
|---|---|---|---|
| `codigo_dimensiones_C.R` | R (.R) | ✅ **Reutilizable** | Crea tres dimensiones básicas: `Dimension_investigadores` (ID único por persona), `Dimension_municipios_de_nacimientos` (COD DANE + geografía de nacimiento) y `Dimension_convocatoria` (3 convocatorias). Exporta en Excel. |
| `dimensiones.ipynb` | Jupyter (.ipynb) | ✅ **Reutilizable** | Notebook Python que genera tres dimensiones adicionales: `Dim_Universidad` (2.983 entidades), `Dim_Formacion` (11 niveles) y `Dim_Residencia` (224 combinaciones únicas). Incluye outputs de ejecución visibles. |
| `tabla_hechos_codigo.R` | R (.R) | ✅ **Reutilizable** | Crea la tabla de hechos del modelo estrella uniendo la base consolidada con las dimensiones de universidad y género. Genera `Tabla_hechos.xlsx`. |
| `README.md` | Markdown | 📄 **Documentación** | Describe cada dimensión creada: filas, columnas, variables incluidas y proceso de deduplicación. |

**Notas de reutilización:**
- Los dos scripts de dimensiones (R y Python) son complementarios; en conjunto cubren todas las dimensiones del modelo.
- Las rutas de entrada deben actualizarse para apuntar a la base limpia (output de `tarea_tabla`).

---

## 5. `tarea_gran_tabla/`

Carpeta con la construcción de la tabla analítica desnormalizada ("gran tabla") y sus análisis.

| Archivo | Tipo | Clasificación | Descripción |
|---|---|---|---|
| `codigo_creacion_gran_tabla_a_partir_del_modelo_estrella.py` | Python (.py) | ✅ **Reutilizable** | Carga automáticamente todos los archivos de un directorio, detecta la tabla de hechos, realiza left joins con las dimensiones usando heurísticas de llaves, exporta `gran_tabla.xlsx/csv` y `gran_tabla_sin_id.xlsx/csv` (sin columnas de IDs). |
| `codigo_analisis_univariado.py` | Python (.py) | ✅ **Reutilizable** | Análisis univariado completo sobre la gran tabla: estadísticos descriptivos de variables numéricas, histogramas, boxplots, tablas de frecuencias para categóricas y distribución temporal por año de convocatoria. |
| `analisis2_(1).ipynb` | Jupyter (.ipynb) | ✅ **Reutilizable** | Notebook con análisis bivariado y pruebas estadísticas: correlación de Spearman, chi-cuadrado (clasificación × región, formación × región, convocatoria × área), Kruskal-Wallis y prueba post-hoc de Dunn. Incluye outputs de ejecución. |
| `analisis_de_clusters.R` | R (.R) | ✅ **Reutilizable** | Aplica K-Prototypes (k=3) sobre variables mixtas (numéricas + categóricas), asigna clústeres y compara perfiles por gran área, género, región, formación, clasificación y edad promedio. |
| `analisis_multivariado_base_gran_table.R` | R (.R) | ✅ **Reutilizable** | Ejecuta Análisis de Correspondencia Simple (CA) para tres pares de variables, Análisis de Correspondencia Múltiple (MCA) con variables de diversidad, y Análisis Factorial de Datos Mixtos (FAMD). Incluye gráficos con `ggplot2` + `ggrepel`. |
| `analisis2.ipynb` | Python (.py disfrazado de .ipynb) | 🗑️ **Descartar** | Archivo con extensión `.ipynb` pero con formato de script Python exportado desde Colab. Contiene un subconjunto del análisis de `analisis2_(1).ipynb` sin outputs ni estructura de celdas JSON. Está completamente **superado** por `analisis2_(1).ipynb`. |
| `analisis_Univariado.md` | Markdown | 📄 **Documentación** | Informe narrativo del análisis univariado con estadísticos, tablas e imágenes incrustadas de GitHub. |
| `informe_clusters.md` | Markdown | 📄 **Documentación** | Informe de los tres clústeres identificados (K-Prototypes): perfiles de área, localización y edad promedio. |
| `informe_multivariado.md` | Markdown | 📄 **Documentación** | Informe de los análisis CA, MCA y FAMD con justificación metodológica, conclusiones por análisis y limitaciones encontradas. |

**Notas de reutilización:**
- `analisis2_(1).ipynb` es la versión consolidada y ejecutada del análisis bivariado; debe mantenerse.
- `analisis2.ipynb` no es un notebook Jupyter válido (falla la validación JSON) y repite código ya presente en `analisis2_(1).ipynb`; puede eliminarse sin pérdida de información.
- El script de creación de la gran tabla (`codigo_creacion_gran_tabla_a_partir_del_modelo_estrella.py`) es genérico y puede adaptarse a nuevos modelos estrella cambiando solo la carpeta de entrada y las `claves_forzadas`.

---

## Resumen de clasificación por archivo

### ✅ Reutilizables (13 archivos)

| # | Archivo | Carpeta | Lenguaje | Propósito principal |
|---|---|---|---|---|
| 1 | `codigo_join.py` | `tarea_join` | Python | Consolidación de bases (2017, 2019, 2021) |
| 2 | `arreglar_base_consultoria_7.R` | `tarea_tabla` | R | Deduplicación de IDs por convocatoria más reciente |
| 3 | `inv_17_codigo_graficas.R` | `tarea_anlisis_bases_de_datos` | R | EDA completo de la base 2017 |
| 4 | `2019_codigo.py` | `tarea_anlisis_bases_de_datos` | Python | EDA completo de la base 2019 |
| 5 | `datos_2021.ipynb` | `tarea_anlisis_bases_de_datos` | Python (Jupyter) | EDA completo de la base 2021 |
| 6 | `codigo_dimensiones_C.R` | `tarea_dimensiones_y_hechos` | R | Generación de dimensiones básicas del modelo estrella |
| 7 | `dimensiones.ipynb` | `tarea_dimensiones_y_hechos` | Python (Jupyter) | Generación de dimensiones de universidad, formación y residencia |
| 8 | `tabla_hechos_codigo.R` | `tarea_dimensiones_y_hechos` | R | Generación de tabla de hechos |
| 9 | `codigo_creacion_gran_tabla_a_partir_del_modelo_estrella.py` | `tarea_gran_tabla` | Python | Construcción de la gran tabla analítica desnormalizada |
| 10 | `codigo_analisis_univariado.py` | `tarea_gran_tabla` | Python | Análisis univariado de la gran tabla |
| 11 | `analisis2_(1).ipynb` | `tarea_gran_tabla` | Python (Jupyter) | Análisis bivariado y pruebas estadísticas |
| 12 | `analisis_de_clusters.R` | `tarea_gran_tabla` | R | Análisis de agrupamiento K-Prototypes |
| 13 | `analisis_multivariado_base_gran_table.R` | `tarea_gran_tabla` | R | Análisis CA, MCA y FAMD |

### 🗑️ Descartar (5 archivos)

| # | Archivo | Carpeta | Motivo |
|---|---|---|---|
| 1 | `graficos_2019/faltantes.png` | `tarea_anlisis_bases_de_datos` | Salida estática regenerable desde `2019_codigo.py` |
| 2 | `graficos_2019/genero.png` | `tarea_anlisis_bases_de_datos` | Salida estática regenerable desde `2019_codigo.py` |
| 3 | `graficos_2019/gran_area.png` | `tarea_anlisis_bases_de_datos` | Salida estática regenerable desde `2019_codigo.py` |
| 4 | `graficos_2019/gran_area_gener.png` | `tarea_anlisis_bases_de_datos` | Salida estática regenerable desde `2019_codigo.py` |
| 5 | `analisis2.ipynb` | `tarea_gran_tabla` | Archivo `.ipynb` inválido (Python script); superado por `analisis2_(1).ipynb` |

### 📄 Documentación / Informes (7 archivos — conservar como referencia)

| # | Archivo | Carpeta | Contenido |
|---|---|---|---|
| 1 | `analisis_17.md` | `tarea_anlisis_bases_de_datos` | Informe EDA base 2017 con interpretaciones y gráficas |
| 2 | `2019_analisis.md` | `tarea_anlisis_bases_de_datos` | Informe EDA base 2019 con gráficas y conclusiones |
| 3 | `README.md` | `tarea_dimensiones_y_hechos` | Descripción de dimensiones del modelo estrella |
| 4 | `README.md` | `tarea_tabla` | Descripción del proceso de deduplicación |
| 5 | `analisis_Univariado.md` | `tarea_gran_tabla` | Informe análisis univariado con estadísticos y gráficas |
| 6 | `informe_clusters.md` | `tarea_gran_tabla` | Informe de agrupamiento K-Prototypes (3 clústeres) |
| 7 | `informe_multivariado.md` | `tarea_gran_tabla` | Informe CA, MCA y FAMD con conclusiones metodológicas |

---

## Pipeline de datos sugerido para sprints futuros

El siguiente orden de ejecución define el flujo completo desde los datos crudos hasta los análisis finales:

```
[Datos crudos CSV 2017/2019/2021]
        │
        ▼
1. tarea_join/codigo_join.py
   → Investigadores_Consolidado.xlsx / .csv
        │
        ▼
2. tarea_tabla/arreglar_base_consultoria_7.R
   → Base_sin_duplicados.xlsx  (26.662 registros únicos)
        │
        ├──────────────────────────────────────────────────────┐
        ▼                                                      ▼
3a. tarea_dimensiones_y_hechos/                         3b. tarea_anlisis_bases_de_datos/
    codigo_dimensiones_C.R                                  inv_17_codigo_graficas.R
    dimensiones.ipynb                                       2019_codigo.py
    tabla_hechos_codigo.R                                   datos_2021.ipynb
    → Modelo estrella                                       → EDA por convocatoria
        │
        ▼
4. tarea_gran_tabla/codigo_creacion_gran_tabla_a_partir_del_modelo_estrella.py
   → GRAN_TABLA(SIN ID).xlsx / .csv  (50.891 registros, 23 variables)
        │
        ├──────────────────────────────────────────────────────┐
        ▼                                                      ▼
5a. Análisis univariado                               5b. Análisis avanzado
    codigo_analisis_univariado.py                         analisis2_(1).ipynb
                                                          analisis_de_clusters.R
                                                          analisis_multivariado_base_gran_table.R
```
