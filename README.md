# Informe de Viabilidad para el Observatorio de Ciencia, Tecnología e Innovación

---

# Introduccion

El presente proyecto se centra en el análisis de datos abiertos relacionados con los investigadores reconocidos en Colombia por convocatorias nacionales de ciencia, tecnología e innovación. Su propósito es consolidar, evaluar y explorar
información estratégica sobre la trayectoria académica, logros científicos,
distribución geográfica e institucional de los investigadores.

En este proyecto, los “Investigadores Reconocidos por Convocatoria” son los
profesionales destacados por el Ministerio de Ciencia, Tecnología e Innovación de
Colombia (Minciencias) mediante convocatorias nacionales. Estos
reconocimientos se otorgan en diversas categorías, considerando criterios como la
producción científica, la formación de recursos humanos, la transferencia de
conocimiento y la participación en redes de colaboración.

Como insumos principales los datasets correspondientes a las convocatorias 2017, 2019
y 2021, disponibles en el portal de Datos Abiertos del Gobierno de Colombia y
Minciencias.

Este proyecto, busca aprovechar estas bases de datos para:

- Consolidar diagnósticos sobre la distribución de investigadores reconocidos
por convocatoria, área de conocimiento e institución.

- Analizar la cobertura geográfica y territorial de los reconocimientos,
identificando posibles concentraciones o vacíos en regiones específicas.

- Comparar las convocatorias de 2017, 2019 y 2021 para evaluar tendencias en la
asignación de reconocimientos y detectar cambios en la política de estímulo
a la investigación.

- Generar visualizaciones y tableros de control que permitan monitorear la
evolución de la investigación reconocida, apoyando la planificación
estratégica y la formulación de políticas en el ámbito científico.

---

# Observatorio de Ciencia, Tecnología e Innovación

## 1. Bases de Datos Seleccionadas
Se trabajará con dos bases de datos provenientes de Minciencias – Colombia, correspondientes a los años 2017, 2019 y 2021, que recopilan información sobre proyectos de investigación e investigadores.  
Ambas bases tienen la misma estructura de 30 variables, lo que permite hacer análisis comparativos y una fusión longitudinal.

## 2. Descripción general
Las bases corresponden a los resultados de convocatorias de reconocimiento de investigadores realizadas por el Ministerio de Ciencia, Tecnología e Innovación de Colombia (Minciencias).  
En ellas se listan los investigadores que han sido clasificados y reconocidos oficialmente de acuerdo con criterios de producción científica, vinculación a grupos de investigación y trayectoria académica.  

Cada dataset incluye información detallada del investigador, del grupo de investigación al que pertenece y de las categorías asignadas en la convocatoria.

## 3. Diccionario de variables
| Nombre de la columna     | Descripción                                                                                  | Tipo de Dato |
|--------------------------|----------------------------------------------------------------------------------------------|--------------|
| ID_CONVOCATORIA          | Identificador de la convocatoria                                                             | Número       |
| NME_CONVOCATORIA         | Nombre de la convocatoria                                                                    | Texto        |
| ANO_CONVO                | Año de realización de la convocatoria                                                        | Marca de tiempo variable |
| ID_PERSONA_PR            | Identificador de la persona                                                                  | Texto        |
| ID_AREA_CON_PR           | Identificador de área de conocimiento OCDE principal del investigador                        | Texto        |
| NME_ESP_AREA_PR          | Especialidad del área de conocimiento OCDE principal del investigador                        | Texto        |
| NME_AREA_PR              | Área de conocimiento OCDE principal del investigador                                         | Texto        |
| NME_GRAN_AREA_PR         | Gran área de conocimiento OCDE principal del investigador                                    | Texto        |
| NME_GENERO_PR            | Género del investigador                                                                     | Texto        |
| NME_PAIS_NAC_PR          | País de nacimiento del investigador                                                          | Texto        |
| NME_REGION_NAC_PR        | Región de nacimiento del investigador                                                        | Texto        |
| NME_DEPARTAMENTO_NAC_PR  | Departamento de nacimiento del investigador                                                  | Texto        |
| NME_MUNICIPIO_NAC_PR     | Municipio de nacimiento del investigador                                                     | Texto        |
| COD_DANE_NAC_PR          | Código de homologación DANE para el municipio de nacimiento                                  | Texto        |
| ID_NIV_FORMACION_PR      | Nivel de formación máximo alcanzado                                                          | Texto        |
| NME_NIV_FORM_PR          | Nombre del nivel de formación máximo alcanzado                                               | Texto        |
| NRO_ORDEN_FORM_PR        | Importancia del nivel de formación, siendo 0 la de menor valor                               | Número       |
| ID_CLAS_PR               | Categoría alcanzada por el investigador                                                      | Texto        |
| NME_CLASIFICACION_PR     | Nombre de la categoría alcanzada por el investigador                                         | Texto        |
| ORDEN_CLAS_PR            | Orden de importancia de la categoría alcanzada por el investigador                           | Número       |
| EDAD_ANOS_PR             | Edad en años desde la fecha de nacimiento hasta el último mes de la convocatoria (2017-07)   | Número       |
| NME_PAIS_RES_PR          | País de ubicación del investigador                                                           | Texto        |
| NME_REGION_RES_PR        | Región de ubicación del investigador                                                         | Texto        |
| NME_DEPARTAMENTO_RES_PR  | Departamento de ubicación del investigador                                                   | Texto        |
| NME_MUNICIPIO_RES_PR     | Municipio de ubicación del investigador                                                      | Texto        |
| COD_DANE_RES_PR          | Código DANE para el municipio de ubicación del investigador                                  | Texto        |
| ID_VICTIMA_CONFLICTO     | Población víctima del conflicto armado                                                       | Texto        |
| TXT_GRUPO_ETNICO         | Grupo étnico del investigador                                                                | Texto        |
| TXT_POBLACION_DISCA      | Población en situación de discapacidad                                                       | Texto        |
| INST_FILIA               | Lista de instituciones que el investigador indica tener filiación separados por PIPE (inst_filia) | Texto |

### Número de registros:
- 2017: 13001  
- 2019: 16796  
- 2021: 21094  

## 4. Calidad de los datos
**Fortalezas:**
- Cobertura de proyectos registrados en convocatorias oficiales.
- Todas las bases tienen el mismo número de columnas y el mismo diccionario de datos.
- Identificadores únicos permiten trazabilidad de proyectos e investigadores.

**Debilidades:**
- Los campos de texto largos presentan variabilidad y requieren limpieza.
- Posibles valores faltantes.
- Algunos proyectos pueden estar duplicados si se registran en más de una convocatoria.

## 5. Acceso y vías de consulta
- **Fuente:** Plataforma de información de [Minciencias](https://minciencias.gov.co/ciudadano/datosabiertos) y Datos Abiertos Colombia. 
- **Formato disponible:** CSV, XLSX.  
- **Acceso:** Descarga libre en línea, no requiere autenticación.  
- **Periodicidad:** Datos reportados con corte anual.  

---

# Informe de Viabilidad para el Observatorio de Ciencia, Tecnología e Innovación

## 1. Accesibilidad y disponibilidad
Los portales de Minciencias y Datos.gov.co ofrecen información pública de acceso abierto, disponible en formatos descargables (CSV, Excel) y mediante API (solo 1000 observaciones).  
Esto asegura facilidad de consulta y de integración entre las 3 bases de datos seleccionadas.

## 2. Alcance temático
La información cubre ejes estratégicos como:  
Investigadores reconocidos de la república de Colombia: por número de convocatoria o año, departamento, genero, especialidad del área de conocimiento OCDE, y entre otros.  

Este alcance permite construir un panorama integral de los investigadores de ciencia en la República de Colombia.

## 3. Posibilidades de articulación
La estructura de los datos permite conectar distintas fuentes gracias a variables comunes (códigos de institución, clasificación por áreas, ubicación geográfica).  
De esta forma, es viable cruzar información entre grupos generando análisis más profundos y comparativos.

## 4. Aplicaciones estratégicas
El uso de estos datasets dentro del Observatorio permitiría:
- Monitorear la evolución y el conteo de los investigadores.
- Observar la proporción territorial de los investigadores.
- Detectar brechas regionales y temáticas en producción de investigadores.
- Elaborar tableros de control interactivos para visualización de tendencias.

## 5. Fundamentación
El carácter oficial y validado de estas fuentes garantiza confiabilidad y pertinencia.  
Además, la actualización periódica (anual) permite mantener indicadores vivos que sirven como insumo para la planeación, la evaluación y la rendición de cuentas en el sector de ciencia y tecnología, con respecto a los investigadores reconocidos de la República de Colombia.

## 6. Sugerencias de implementación
1. Depurar variables redundantes: Para tener que operar con las variables necesarias y no consumir espacio en dos variables que expliquen algo similar.  
2. Análisis de datos faltantes:  
   - Revisión de inconsistencias y valores faltantes.  
   - Validación de identificadores de instituciones y regiones.  
   - Homologación de clasificaciones temáticas.  
3. Integración de los datasets: Crear un solo dataset que contenga las tres convocatorias hechas por el Estado Colombiano de reconocimiento de investigadores.  

## 7. Conclusión
La integración de los datasets de Minciencias y Datos.gov.co sobre lo investigadores reconocidos por fecha de convocatoria o año, es altamente viable.  
Estos recursos ofrecen una base sólida para consolidar el Observatorio de Ciencia, Tecnología e Innovación, permitiendo producir análisis comparativos, identificar tendencias y orientar decisiones de política pública en el país.

