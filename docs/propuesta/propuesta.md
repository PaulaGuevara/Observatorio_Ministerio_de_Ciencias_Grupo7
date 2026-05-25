# Propuesta del proyecto

## Análisis regional de la producción científica en Colombia

**Proyecto:** Integración de bases de Minciencias para el análisis regional de la producción científica  
**Convocatorias:** 2017, 2019 y 2021  
**Integrantes:** Maria Paula Amaya y Paula Bentancourt  
**Universidad:** Universidad Santo Tomás  
**Facultad:** Estadística  

---

## 1. Planteamiento del problema

Minciencias publica información relevante sobre productos científicos, grupos de investigación e investigadores reconocidos. Sin embargo, esta información se encuentra distribuida en diferentes archivos y convocatorias, lo que dificulta analizar de forma integrada cómo se distribuye la producción científica en Colombia.

El problema principal del proyecto es que la información se encuentra fragmentada. Los productos científicos, los investigadores y los grupos de investigación están en bases separadas, por lo que no es inmediato responder preguntas relacionadas con qué se produce, quién participa y dónde se ubica territorialmente la producción científica registrada.

Además, el volumen de datos supera el límite práctico de herramientas como Excel, por lo que se requiere un proceso de integración y análisis más eficiente, usando herramientas computacionales que permitan consolidar, transformar y consultar la información.

---

## 2. Pregunta de investigación

¿Cómo se distribuye regionalmente la producción científica registrada en Minciencias en las convocatorias 2017, 2019 y 2021, tomando como eje principal la ubicación de los grupos de investigación y, de manera complementaria, la información territorial de los investigadores cuando el cruce de datos lo permite?

---

## 3. Objetivo general

Analizar la distribución regional de la producción científica registrada en Minciencias mediante la integración de bases de productos, investigadores y grupos de investigación, para construir métricas territoriales de volumen, participación, clasificación, diversidad, crecimiento y consolidación.

---

## 4. Objetivos específicos

- Integrar las bases de productos, investigadores reconocidos y grupos de investigación para las convocatorias 2017, 2019 y 2021.
- Validar duplicados, correspondencias y conservación de productos durante el proceso de integración.
- Construir una base analítica consolidada en formato eficiente para consulta y análisis.
- Calcular indicadores regionales que permitan comparar la producción científica entre territorios.
- Diferenciar el análisis por ubicación del grupo de investigación y por ubicación del investigador cuando exista cruce válido.
- Construir visualizaciones y tableros que permitan interpretar la distribución territorial de la producción científica.

---

## 5. Fuentes de información

Se utilizaron bases públicas de Minciencias asociadas a las convocatorias 2017, 2019 y 2021. Las fuentes se organizan en tres grupos principales:

### 5.1 Producción científica

Aporta la información de los productos registrados, incluyendo clase de producto, tipo de medición, tipología, categoría y código del grupo asociado.

### 5.2 Investigadores reconocidos

Aporta información relacionada con las personas reconocidas como investigadores, incluyendo género, nivel de formación, clasificación, residencia, pertenencia étnica y discapacidad.

### 5.3 Grupos de investigación

Aporta el contexto institucional y territorial del grupo, incluyendo institución avaladora, clasificación del grupo, país, región, departamento y municipio.

---

## 6. Unidad de análisis

La unidad de análisis principal del proyecto es el producto científico asociado a un grupo de investigación.

Cada fila de la base consolidada representa un producto científico registrado en una convocatoria. El producto se asocia a un grupo mediante el código del grupo y la convocatoria. Cuando existe coincidencia válida por identificador de persona, se agrega información del investigador.

Esta definición evita confundir la base final con una base únicamente de personas o únicamente de grupos. El centro del análisis es la producción científica, pero enriquecida con información institucional, territorial y de investigadores.

---

## 7. Proceso de integración

El proceso de integración se realizó mediante los siguientes pasos:

1. Consolidación de investigadores reconocidos por convocatoria.
2. Deduplicación de investigadores usando identificador de persona y convocatoria.
3. Integración de productos científicos de las convocatorias 2017, 2019 y 2021.
4. Cruce de productos con investigadores mediante `ID_PERSONA_PD`, `ID_PERSONA_PR` e `ID_CONVOCATORIA`.
5. Cruce de productos con grupos de investigación mediante `COD_GRUPO_GR` e `ID_CONVOCATORIA`.
6. Conservación de todos los productos científicos mediante cruces tipo `LEFT JOIN`.
7. Exportación de la base consolidada en formato Parquet para mejorar eficiencia de almacenamiento y consulta.

El uso de `LEFT JOIN` permite conservar todos los productos aunque no todos tengan coincidencia válida con investigadores o grupos. Esto es importante porque la producción científica es la unidad principal del análisis.

---

## 8. Resultado de la base consolidada

La integración permitió construir una base analítica con las siguientes características generales:

- 2.209.409 registros consolidados.
- 33 variables finales.
- 3 convocatorias integradas: 2017, 2019 y 2021.
- 17.139 grupos únicos.
- Salida principal en formato Parquet.
- Evidencia de validación mediante archivo de resumen.
- Muestra revisable en Excel para facilitar inspección manual.

---

## 9. Variables clave

Las variables se organizan en tres dimensiones analíticas:

### 9.1 Producto científico

- `ID_PERSONA_PD`
- `NME_CLASE_PD`
- `NME_TIPO_MEDICION_PD`
- `NME_TIPOLOGIA_PD`
- `ID_TIPO_PD_MED`
- `NME_CATEGORIA_PD`
- `COD_GRUPO_GR`

Estas variables permiten caracterizar qué tipo de producción científica se registra.

### 9.2 Investigador

- `ID_PERSONA_PR`
- `NME_GENERO_PR`
- `NME_NIV_FORM_PR`
- `NME_CLASIFICACION_PR`
- `EDAD_ANOS_PR`
- `NME_DEPARTAMENTO_RES_PR`
- `NME_REGION_RES_PR`

Estas variables permiten estudiar el perfil y la ubicación de los investigadores cuando el cruce con productos es válido.

### 9.3 Grupo e institución

- `COD_GRUPO_GR`
- `INST_AVAL`
- `NME_CLASIFICACION_GR`
- `NME_PAIS_GR`
- `NME_REGION_GR`
- `NME_DEPARTAMENTO_GR`
- `NME_MUNICIPIO_GR`

Estas variables permiten ubicar territorial e institucionalmente la producción científica.

---

## 10. Indicadores considerados para el proyecto

A partir de la base consolidada se plantean y calculan algunos indicadores regionales para analizar la producción científica desde diferentes dimensiones. Estos indicadores no buscan replicar la clasificación oficial completa de Minciencias, sino caracterizar la distribución regional de la producción, la participación territorial, la productividad media, la clasificación de los grupos, la diversidad, la permanencia, el crecimiento y la consolidación.

Los siguientes 16 indicadores son algunos de los indicadores que se van a tener en cuenta dentro del proyecto:

| No. | Indicador | Descripción | Archivo de salida esperado |
|---:|---|---|---|
| 1 | Producción total por región | Cuenta el número total de productos científicos asociados a cada región. | `01_produccion_total_region_match.csv` |
| 2 | Participación porcentual regional | Calcula el peso porcentual de cada región frente al total nacional de productos. | `02_participacion_region_match.csv` |
| 3 | Producción promedio por grupo | Mide el promedio de productos por grupo de investigación en cada región. | `03_promedio_por_grupo_match.csv` |
| 4 | Producción por clasificación del grupo | Cuenta productos por región según la clasificación del grupo, por ejemplo A1, A, B o C. | `04_produccion_clasificacion_region_match.csv` |
| 5 | Diversidad de producción científica | Cuenta cuántas tipologías distintas de productos aparecen en cada región. | `05_diversidad_region_match.csv` |
| 6 | Índice de especialización productiva | Identifica si una región concentra su producción en ciertas tipologías frente al comportamiento general. | `06_indice_especializacion_productiva_match.csv` |
| 7 | Diversidad relativa regional | Compara la diversidad de tipologías de cada región frente a su volumen de producción. | `07_diversidad_relativa_region_match.csv` |
| 8 | Permanencia de grupos por región | Identifica grupos que permanecen en más de una convocatoria dentro de cada región. | `08_permanencia_grupos_region_match.csv` |
| 9 | Crecimiento de grupos por región | Analiza la variación de grupos entre convocatorias por región. | `09_crecimiento_grupos_region_match.csv` |
| 10 | Consolidación de grupos por región | Resume estabilidad o continuidad de los grupos regionales en el periodo analizado. | `10_consolidacion_grupos_region_match.csv` |
| 11 | Renovación de grupos por región | Identifica entrada o aparición de grupos nuevos en las convocatorias analizadas. | `11_renovacion_grupos_region_match.csv` |
| 12 | Distribución por género y región | Caracteriza la participación de investigadores según género y región cuando el cruce es válido. | `12_genero_region_match.csv` |
| 13 | Evolución detallada de grupos | Presenta el comportamiento de grupos por convocatoria con mayor detalle. | `13_evolucion_grupos_detalle_match.csv` |
| 14 | Evolución de grupos por región | Resume la evolución regional de los grupos entre 2017, 2019 y 2021. | `14_evolucion_grupos_region_match.csv` |
| 15 | Participación por clasificación del grupo | Calcula la participación de productos según clasificación del grupo dentro de cada región. | `15_participacion_clasificacion_region_match.csv` |
| 16 | Participación por clasificación, región y convocatoria | Analiza la participación de productos por clasificación del grupo, región y año de convocatoria. | `16_participacion_clasificacion_region_convocatoria_match.csv` |

---

## 11. Perspectivas territoriales del análisis

El proyecto considera dos perspectivas territoriales:

### 11.1 Ubicación del grupo de investigación

Es el eje principal del análisis. Cada producto se asigna al territorio del grupo de investigación, usando variables como región, departamento o municipio del grupo. Esta perspectiva es la más estable porque la base de productos está asociada directamente a grupos.

### 11.2 Ubicación del investigador

Es una dimensión complementaria. Se usa únicamente cuando el identificador de persona permite cruzar de manera válida la base de productos con la base de investigadores reconocidos.

Esta diferencia es importante porque un producto puede estar asociado a un grupo ubicado en una región, mientras que el investigador puede residir en otra. Por eso, la ubicación del grupo se toma como eje principal y la ubicación del investigador como análisis complementario.

---

## 12. Resultados esperados

Se espera obtener:

- Una base consolidada y trazable de producción científica.
- Indicadores regionales comparables entre convocatorias.
- Archivos CSV con los resultados de cada métrica.
- Visualizaciones regionales claras y ejecutivas.
- Un dashboard que permita analizar la distribución territorial de la producción científica.
- Evidencia metodológica de la integración, validación y cálculo de indicadores.

---

## 13. Alcance y limitaciones

El proyecto tiene un alcance descriptivo y analítico. Permite caracterizar la distribución regional de la producción científica registrada en las bases utilizadas, pero no pretende reemplazar el modelo oficial de medición de Minciencias.

Las principales limitaciones son:

- No todos los productos tienen coincidencia válida con investigadores.
- La ubicación principal del análisis corresponde al grupo de investigación, no necesariamente al lugar de residencia del investigador.
- Las métricas calculadas son descriptivas y no implican causalidad.
- La clasificación del grupo se usa como variable de análisis, pero no se recalcula la clasificación oficial de Minciencias.
- La calidad del análisis depende de la consistencia y completitud de las bases originales.

---

## 14. Conclusión

La integración de bases de Minciencias permite transformar información fragmentada en una base analítica útil para estudiar la producción científica desde una perspectiva territorial.

El proyecto permite analizar volumen, participación, productividad promedio, clasificación, diversidad, permanencia, crecimiento y consolidación de la producción científica regional en Colombia durante las convocatorias 2017, 2019 y 2021.

El valor principal del proyecto está en construir una base trazable, eficiente y útil para visualizar y comparar la distribución territorial de la ciencia en Colombia.
