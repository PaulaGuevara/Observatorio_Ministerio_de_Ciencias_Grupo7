# Marco Teórico: Modernización del Observatorio MinCiencias
> **Proyecto:** Diseño de Arquitectura de Datos para el Ministerio de Ciencia, Tecnología e Innovación.
> **Grupo:** 2 -Observatorio MiniCiencias- Consultoría e Investigación .

---
## 1. Introducción al Business Intelligence (BI) en el Sector Público
El desarrollo de un Observatorio de Ciencia, Tecnología e Innovación (CTeI) requiere la transición de datos transaccionales a **datos analíticos**. La inteligencia de negocios permite al Ministerio transformar registros administrativos en conocimiento estratégico para la toma de decisiones gubernamentales.

## 2. Modelado Multidimensional
El análisis utiliza la clasificación oficial que otorga MinCiencias tras cada convocatoria nacional:
* **Grupos:** Clasificados en categorías **A1, A, B, C o Reconocidos**, según su índice de producción y estabilidad.
* **Investigadores:** Clasificados como **Senior, Asociado o Junior**, dependiendo de su trayectoria y productos de nuevo conocimiento.


### 2.1 Tablas de Hechos (Fact Tables)
Representan los procesos de negocio que queremos medir. En el contexto de MinCiencias, un "hecho" puede ser:
* La asignación de una beca.
* El registro de un nuevo artículo de investigación.
* La ejecución presupuestal de un proyecto.

### 2.2 Tablas de Dimensiones (Dimension Tables)
Son los filtros o "perspectivas" a través de las cuales analizamos los hechos. Las dimensiones clave identificadas son:
* **Dimensión Geográfica:** Departamentos y municipios de Colombia (Basado en códigos DANE).
* **Dimensión Investigador:** Categorización (Senior, Asociado, Junior, Integrante).
* **Dimensión Tiempo:** Permite análisis de tendencias interanuales.
* **Dimensión Área del Conocimiento:** Clasificación según la OCDE (Ciencias Naturales, Ingeniería, Médicas, etc.).

Para la tarea de **Dimensiones y Hechos**, el marco conceptual se apoya en el diseño de un bus de datos que permita filtrar la información por:
* **Dimensión Institución:** Clasificación de universidades y centros de investigación (Públicas vs. Privadas).
* **Dimensión Geográfica:** Distribución de la ciencia por departamentos y regiones.
* **Hechos (Facts):** Conteo de productos, número de integrantes activos y años de existencia del grupo.

## 3. Arquitectura de Datos: Esquema Estrella
Se ha seleccionado el **Esquema Estrella (Star Schema)** por su eficiencia en entornos de consulta. En este modelo, una tabla de hechos central está conectada directamente con sus dimensiones, reduciendo la complejidad de las consultas SQL y optimizando el rendimiento de las herramientas de visualización.

## 4. Procesos ETL (Extract, Transform, Load)
El éxito del Observatorio depende de la calidad del dato. El marco teórico contempla tres etapas críticas:
1.  **Extracción:** Conexión a fuentes como *Scienti*, *GrupLAC* y bases de datos internas.
2.  **Transformación:** Normalización de nombres de instituciones, manejo de registros duplicados y estandarización de formatos de fecha.
3.  **Carga:** Inserción de datos limpios en el modelo de producción.

## 5. Indicadores de Impacto Científico (KPIs)
El modelo debe permitir el cálculo de indicadores estandarizados internacionalmente:
* **Tasa de crecimiento de investigadores:** Variación porcentual de capital humano calificado.
* **Inversión en I+D (Investigación y Desarrollo):** Distribución de recursos por región.
* **Producción por Área:** Densidad de artículos y patentes por disciplina.

## 6. Analítica de Datos y Visualización
Se fundamenta en el uso de herramientas de código abierto para el procesamiento de grandes volúmenes de datos provenientes de plataformas como Scienti:
* **Python (Pandas/NumPy):** Para la limpieza y normalización de nombres de instituciones y grupos.
* **Análisis Descriptivo:** Para identificar brechas de género en la investigación y disparidades regionales en la inversión de CTeI.

---
*Este documento es parte de la entrega de la tarea de Marco teorico del Grupo 2.*