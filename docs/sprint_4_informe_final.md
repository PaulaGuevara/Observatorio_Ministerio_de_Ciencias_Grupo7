# Informe Final Reproducible — Sprint 4  
## Observatorio de Investigadores Reconocidos por Minciencias — Grupo 7

**Fecha:** Abril 2026  
**Fuente principal:** `datos/tarea_join/investigadores_consolidado.csv`  
**Convocatorias analizadas:** 2017, 2019, 2021  
**Portal de referencia:** [datos.gov.co — Investigadores Reconocidos por convocatoria](https://www.datos.gov.co/Ciencia-Tecnolog-a-e-Innovaci-n/Investigadores-Reconocidos-por-convocatoria/bqtm-4y2h/about_data)

---

## Resumen ejecutivo

Este informe integra los hallazgos de los cuatro sprints del proyecto. A partir de las bases de investigadores reconocidos por Minciencias (2017, 2019 y 2021), se realizaron: (1) análisis longitudinal de trayectorias individuales y matrices de transición entre categorías; (2) análisis de concentración territorial mediante el índice Herfindahl-Hirschman; (3) análisis de redes de co-filiación institucional; y (4) análisis de variables de conflicto, etnia y discapacidad con comparación frente al Censo DANE 2018. Los resultados muestran un sistema de investigación con alta permanencia en categorías intermedias, fuerte concentración territorial en tres departamentos, una red de colaboración institucional con estructura de hub dominado por la Universidad Nacional, y brechas sistemáticas de representación para poblaciones en condición de vulnerabilidad.

---

## 1. Introducción

El sistema colombiano de reconocimiento de investigadores opera bajo convocatorias periódicas de Minciencias, cuyos registros permiten estudiar la evolución del capital humano científico del país. El presente trabajo consolida y analiza dichos registros buscando responder cuatro preguntas analíticas transversales: ¿cómo cambia la categoría de un investigador entre convocatorias consecutivas?, ¿qué tan concentrada geográficamente está la investigación reconocida?, ¿qué estructura de colaboración institucional emerge de las co-filiaciones declaradas?, y ¿en qué medida la comunidad investigadora refleja la diversidad étnica, de discapacidad y de exposición al conflicto armado de la población general?

La base de trabajo es el consolidado único de las convocatorias 2017, 2019 y 2021, construido mediante la unión de las tres tablas originales con verificación heurística de unicidad de `ID_PERSONA_PR`. La convocatoria 2023 no se incluye porque a la fecha de análisis no ha sido publicada oficialmente en el portal de datos abiertos del gobierno (última actualización disponible: septiembre 2022).

---

## 2. Materiales y métodos

### 2.1 Fuente de datos

| Convocatoria | Registros | Variables clave de diversidad disponibles |
|:---:|---:|:---|
| 2017 | 13 001 | No disponibles |
| 2019 | 16 796 | No disponibles |
| 2021 | 21 094 | `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO`, `TXT_POBLACION_DISCA` (96.8 % con valor útil) |

La ausencia de variables de diversidad en 2017 y 2019 es estructural: dichos campos no formaban parte del formulario de esas convocatorias. El análisis de diversidad se circunscribe, por tanto, a 2021.

### 2.2 Variables utilizadas

| Variable | Rol analítico |
|:---|:---|
| `ID_PERSONA_PR` | Identificador longitudinal del investigador |
| `ANO_CONVO` | Año de la convocatoria (transformado desde fecha) |
| `NME_CLASIFICACION_PR` | Categoría del investigador (Junior, Asociado, Senior, Emérito) |
| `NME_DEPARTAMENTO_RES_PR` | Departamento de residencia |
| `INST_FILIA` | Instituciones de afiliación (separadas por `|`) |
| `NME_GRAN_AREA_PR` | Gran área OCDE del investigador |
| `COD_SEXO_PR` | Sexo del investigador |
| `ID_VICTIMA_CONFLICTO` | Condición de víctima del conflicto armado |
| `TXT_GRUPO_ETNICO` | Grupo étnico autodeclarado |
| `TXT_POBLACION_DISCA` | Tipo de discapacidad autodeclarada |

### 2.3 Métodos aplicados

| Sprint | Método | Herramienta |
|:---|:---|:---|
| 1 — Longitudinal | Seguimiento panel; matrices de transición de Markov | Python / pandas |
| 2 — Territorial | Índice Herfindahl-Hirschman (HHI) | Python / pandas |
| 2 — Género | Comparación de participación femenina por gran área OCDE | Python / pandas |
| 3 — Redes | Grafo de co-filiación (NetworkX); métricas de centralidad | Python / NetworkX |
| 4 — Diversidad | Tablas de frecuencia; comparación de proporciones con DANE 2018 | Python / pandas |

---

## 3. Resultados

### 3.1 Análisis longitudinal de trayectorias (Sprints 1–2)

#### 3.1.1 Resumen de movilidad entre convocatorias

El seguimiento longitudinal se construyó emparejando registros del mismo `ID_PERSONA_PR` en pares de convocatorias consecutivas. Para cada investigador presente en la convocatoria inicial se clasificó su situación al final del periodo.

| Periodo | Total inicial | Se mantiene | Sube | Baja | Desaparece |
|:---:|---:|---:|---:|---:|---:|
| 2017 → 2019 | 13 001 | 7 018 (54.0 %) | 2 246 (17.3 %) | 730 (5.6 %) | 3 007 (23.1 %) |
| 2019 → 2021 | 16 796 | 9 657 (57.5 %) | 2 336 (13.9 %) | 1 362 (8.1 %) | 3 441 (20.5 %) |

**Interpretación.** En ambos periodos la situación dominante es la permanencia en la misma categoría. Los ascensos superan a los descensos en los dos periodos, aunque en 2019→2021 la proporción de ascensos disminuye (17.3 % → 13.9 %) mientras la de descensos aumenta (5.6 % → 8.1 %), lo que sugiere un endurecimiento relativo de las condiciones de ascenso o un efecto pandemia-COVID sobre la producción evaluada. La proporción de investigadores que desaparecen (≈ 20–23 %) refleja la rotación natural del panel, que incluye jubilaciones, cambio de actividad o no presentación voluntaria a la convocatoria siguiente.

#### 3.1.2 Matrices de transición entre categorías

Las matrices de transición se calcularon para investigadores con aparición en ambas convocatorias del periodo. Los valores corresponden a probabilidades de pasar de la categoría de fila a la categoría de columna.

**Periodo 2017 → 2019**

| Origen \ Destino | Junior | Asociado | Senior | Emérito |
|:---|:---:|:---:|:---:|:---:|
| Junior | 0.720 | 0.243 | 0.036 | 0.001 |
| Asociado | 0.181 | 0.580 | 0.235 | 0.004 |
| Senior | 0.050 | 0.056 | 0.877 | 0.018 |

**Periodo 2019 → 2021**

| Origen \ Destino | Junior | Asociado | Senior | Emérito |
|:---|:---:|:---:|:---:|:---:|
| Junior | 0.779 | 0.179 | 0.041 | 0.001 |
| Asociado | 0.250 | 0.564 | 0.182 | 0.004 |
| Senior | 0.037 | 0.132 | 0.812 | 0.019 |

**Hallazgos clave:**

- **Senior** es la categoría más estable (P(permanencia) ≈ 0.88 en 2017→2019; 0.81 en 2019→2021), pero su estabilidad cae 7 puntos porcentuales en el segundo periodo.
- **Junior** presenta alta permanencia (≈ 72–78 %), con la transición ascendente más frecuente hacia Asociado. La movilidad ascendente desde Junior se ralentiza en el segundo periodo (24.3 % → 17.9 % hacia Asociado).
- **Asociado** es la categoría con mayor dinamismo: experimenta movilidad tanto ascendente como descendente. Notoriamente, la probabilidad de descender de Asociado a Junior crece de 18.1 % a 25.0 % entre periodos, señal de que las condiciones de mantenimiento en esta categoría se tornaron más exigentes.
- Las transiciones hacia **Emérito** son posibles pero marginales en todos los casos (< 0.5 %).

---

### 3.2 Concentración territorial — Índice Herfindahl-Hirschman (Sprint 2)

El HHI mide la concentración de una distribución. Se calculó usando la participación de cada departamento como fracción del total de investigadores únicos.

$$
\text{HHI} = \sum_{i=1}^{n} s_i^2
$$

donde $s_i$ es la participación del departamento $i$. El índice se reporta también en escala 0–10 000 ($\text{HHI}_{10000} = \text{HHI} \times 10000$).

| Base | Investigadores | HHI | HHI (0–10 000) | Nivel de concentración |
|:---|---:|:---:|:---:|:---|
| Depurada (persona única) | 26 662 | 0.1518 | 1 517.6 | Moderada |
| Consolidado completo (sin deduplicar) | 50 891 | 0.1532 | 1 531.9 | Moderada |

La deduplicación por persona no altera la conclusión sobre el nivel de concentración, lo que valida la robustez del resultado.

#### Top 5 departamentos de residencia (base depurada)

| Departamento | Investigadores | Participación |
|:---|---:|:---:|
| Bogotá, D. C. | 8 612 | 32.3 % |
| Antioquia | 4 425 | 16.6 % |
| Valle del Cauca | 2 197 | 8.2 % |
| Atlántico | 1 778 | 6.7 % |
| Santander | 1 412 | 5.3 % |

Los tres primeros departamentos concentran el **57.1 %** de los investigadores únicos. En el extremo opuesto, departamentos como Vichada (n = 1), Guaviare (n = 2) y Vaupés (n = 2) tienen presencia mínima, evidenciando una brecha territorial profunda entre regiones con tradición universitaria consolidada y territorios históricamente marginados de la política científica nacional.

---

### 3.3 Participación femenina por gran área OCDE (Sprint 2)

| Gran área OCDE | % femenino 2017 | % femenino 2019 | % femenino 2021 | Cambio 2017–2021 |
|:---|:---:|:---:|:---:|:---:|
| Ingeniería y Tecnología | 25.7 % | 26.0 % | 26.5 % | +0.8 pp |
| Ciencias Agrícolas | 32.9 % | 35.8 % | 35.0 % | +2.2 pp |
| Ciencias Naturales | 34.2 % | 35.3 % | 35.8 % | +1.6 pp |
| Humanidades | 33.1 % | 33.7 % | 38.4 % | +5.3 pp |
| Ciencias Sociales | 43.5 % | 44.1 % | 45.1 % | +1.7 pp |
| Ciencias Médicas y de la Salud | 48.2 % | 48.7 % | 50.8 % | +2.7 pp |

La participación femenina crece en todas las áreas entre 2017 y 2021, aunque a ritmos desiguales. Ingeniería y Tecnología sigue siendo el área con menor representación femenina (≈ 26 %), en contraste con Ciencias Médicas y de la Salud que supera el 50 % en 2021. Humanidades registró el mayor avance relativo (+5.3 pp), señal de un cambio generacional en esa disciplina.

---

### 3.4 Red de co-filiación institucional (Sprint 3)

#### 3.4.1 Descripción del modelo de red

Se construyó un grafo no dirigido donde los **nodos** son instituciones y las **aristas** conectan pares de instituciones que comparten al menos dos investigadores. El peso de cada arista es el número de investigadores en co-filiación. Se normalizaron variantes nominales de una misma institución (sedes, paréntesis, formatos) antes de construir el grafo.

#### 3.4.2 Métricas globales del grafo

| Métrica | Valor |
|:---|:---:|
| Investigadores con al menos una afiliación | 46 618 |
| Investigadores con co-filiación (≥ 2 instituciones) | 537 |
| Porcentaje con co-filiación | 1.15 % |
| Nodos activos (instituciones) | 31 |
| Aristas (co-filiaciones con umbral ≥ 2) | 28 |
| Componentes conectados | 4 |
| Densidad de red | 0.060 |

La baja densidad (0.060) y los cuatro componentes desconectados indican un sistema de colaboración interinstitucional incipiente: la co-filiación es la excepción y no la norma dentro del panel de investigadores reconocidos.

#### 3.4.3 Instituciones con mayor centralidad de grado

| Institución | Investigadores afiliados | Centralidad de grado |
|:---|:---:|:---:|
| Universidad Nacional de Colombia (Sede Bogotá) | 3 453 | 0.367 |
| Universidad de Antioquia | 2 238 | 0.267 |
| Pontificia Universidad Javeriana | 1 825 | 0.133 |
| Universidad de los Andes | 1 175 | 0.067 |
| Universidad EAFIT | 562 | 0.067 |

La **Universidad Nacional de Colombia** actúa como hub dominante de la red: conecta con el mayor número de instituciones distintas y concentra el mayor volumen de investigadores afiliados. La **Universidad de Antioquia** ocupa el segundo lugar, reforzando el eje Bogotá-Antioquia ya identificado en el análisis territorial.

#### 3.4.4 Pares institucionales con mayor co-filiación

| Institución A | Institución B | Investigadores compartidos |
|:---|:---|:---:|
| Universidad Nacional — Sede Bogotá | Universidad de Antioquia | 5 |
| Universidad Nacional — Sede Bogotá | Universidad Industrial de Santander | 3 |
| Universidad Nacional — Sede Bogotá | Universidad de los Andes | 3 |
| Colegio Mayor Ntra. Sra. del Rosario | Universidad del Rosario | 3 |
| Universidad Nacional — Sede Bogotá | Fundación Universidad del Norte | 3 |

La vinculación UNAL-UdeA es la más fuerte del sistema y reproduce en la red de colaboración la misma dualidad territorial observada en la distribución por departamento.

---

### 3.5 Variables de diversidad: conflicto, etnia y discapacidad (Sprint 4)

El análisis se realizó sobre la convocatoria 2021 (n = 21 094), que es la única con registros útiles para las tres variables. Se excluyeron los registros con respuesta "No informa" del cálculo de porcentajes válidos para hacer los valores comparables con estadísticas nacionales del DANE.

#### 3.5.1 Víctimas del conflicto armado

| Categoría | n | % sobre válidos |
|:---|---:|:---:|
| No es víctima | 20 002 | 97.9 % |
| Sí es víctima | 421 | 2.1 % |
| No informa | 671 | — |

**Comparación con DANE 2018:** según la Encuesta Nacional de Calidad de Vida (ECV) 2018, el 11.8 % de la población colombiana declara haber sido víctima del conflicto armado. La comunidad investigadora reconocida presenta una tasa de 2.1 %, lo que representa una **brecha de −9.7 puntos porcentuales**. Esta subrepresentación es consistente con la distribución territorial del conflicto, que afecta principalmente a regiones con baja densidad de investigadores reconocidos (Pacífico, Amazonia, Orinoquía), y con las barreras estructurales de acceso a la educación superior que históricamente han afectado a las poblaciones desplazadas.

#### 3.5.2 Grupo étnico

| Grupo étnico | n | % sobre válidos | % DANE 2018 | Brecha (pp) |
|:---|---:|:---:|:---:|:---:|
| Ningún grupo étnico | 19 674 | 96.3 % | — | — |
| NARP (Negro, Afrocolombiano, Raizal, Palenquero) | 509 | 2.5 % | 9.3 % | −6.8 |
| Blanco o mestizo | 120 | 0.6 % | — | — |
| Indígena | 114 | 0.6 % | 4.4 % | −3.8 |
| Rrom | 6 | 0.03 % | 0.006 % | +0.02 |

La población NARP está subrepresentada en casi 7 puntos porcentuales respecto a su peso en la población general. La población indígena muestra una brecha de −3.8 pp. Estas brechas están correlacionadas con las desigualdades en acceso a educación superior documentadas en Colombia y con la concentración geográfica de la investigación reconocida lejos de los territorios con mayor presencia de estas comunidades.

#### 3.5.3 Discapacidad

| Categoría | n | % sobre válidos | % DANE 2018 | Brecha (pp) |
|:---|---:|:---:|:---:|:---:|
| Sin discapacidad | 20 240 | 99.1 % | 95.8 % | — |
| Con discapacidad | 181 | 0.9 % | 4.24 % | −3.4 |
| No informa | 673 | — | — | — |

Entre los investigadores con alguna discapacidad, los tipos más frecuentes son: visual (n = 68; 0.33 %), física (n = 55; 0.27 %) y auditiva (n = 42; 0.21 %). La prevalencia de discapacidad en la comunidad investigadora (0.9 %) es notablemente menor que la estimada para la población general por el DANE 2018 (4.24 %), con una brecha de −3.4 pp. Esta subrepresentación puede reflejar tanto barreras de acceso al sistema educativo como posibles subregistros en el autoreporte del formulario.

#### 3.5.4 Transcripción íntegra de evidencia Sprint 4 (MariaAmaya12)

Esta sección incorpora de forma reproducible el contenido completo del análisis en `evidencias/sprint4/evidencia_sprint4_variables_dane_2018.md` (rama `develop_mariap`), para dejar trazabilidad textual y numérica exacta.

##### 1. Fuente de entrada

- Archivo analizado: `datos/tarea_join/investigadores_consolidado.csv`
- Año seleccionado para la explotación: **2021**

##### 2. Disponibilidad de variables por año

Se revisaron las convocatorias disponibles y se verificó la disponibilidad de `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO` y `TXT_POBLACION_DISCA`.

| anio | n_registros | ID_VICTIMA_CONFLICTO_n_util | ID_VICTIMA_CONFLICTO_pct_util | TXT_GRUPO_ETNICO_n_util | TXT_GRUPO_ETNICO_pct_util | TXT_POBLACION_DISCA_n_util | TXT_POBLACION_DISCA_pct_util |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 13001 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019 | 16796 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2021 | 21094 | 20423 | 96.82 | 20423 | 96.82 | 20421 | 96.81 |

##### 3. Justificación metodológica

Aunque el proyecto trabaja con 2017, 2019 y 2021, la explotación sustantiva de estas variables se realiza sobre el año con información útil. Si en un año los registros aparecen únicamente como `No registra` o `No disponible`, ese año se documenta, pero no se usa para calcular porcentajes comparables con DANE.

##### 4. Resultados descriptivos

###### 4.1 Víctima del conflicto

| categoria | n | pct_total | pct_validos |
|:---|---:|---:|---:|
| No | 20002 | 94.8232 | 97.9386 |
| No informa | 671 | 3.181 | 0 |
| Sí | 421 | 1.9958 | 2.0614 |

###### 4.2 Grupo étnico

| categoria | n | pct_total | pct_validos |
|:---|---:|---:|---:|
| Ningún grupo étnico | 19674 | 93.2682 | 96.3326 |
| No informa | 671 | 3.181 | 0 |
| NARP | 509 | 2.413 | 2.4923 |
| Blanco o mestizo | 120 | 0.5689 | 0.5876 |
| Indígena | 114 | 0.5404 | 0.5582 |
| Rrom | 6 | 0.0284 | 0.0294 |

###### 4.3 Discapacidad (detalle)

| categoria | n | pct_total | pct_validos |
|:---|---:|---:|---:|
| Ninguna | 20240 | 95.9515 | 99.1137 |
| No informa | 673 | 3.1905 | 0 |
| Visual | 68 | 0.3224 | 0.333 |
| Física | 55 | 0.2607 | 0.2693 |
| Auditiva | 42 | 0.1991 | 0.2057 |
| Psicosocial | 6 | 0.0284 | 0.0294 |
| Intelectual | 6 | 0.0284 | 0.0294 |
| Múltiple | 4 | 0.019 | 0.0196 |

###### 4.4 Discapacidad (binaria)

| categoria | n | pct_total | pct_validos |
|:---|---:|---:|---:|
| No | 20240 | 95.9515 | 99.1137 |
| No informa | 673 | 3.1905 | 0 |
| Sí | 181 | 0.8581 | 0.8863 |

##### 5. Comparación con DANE 2018

###### 5.1 Víctima del conflicto

| indicador | categoria | pct_base | pct_dane_2018 | brecha_pp |
|:---|:---|---:|---:|---:|
| víctima del conflicto | Sí | 2.0614 | 11.8 | -9.7386 |

###### 5.2 Discapacidad

| indicador | categoria | pct_base | pct_dane_2018 | brecha_pp |
|:---|:---|---:|---:|---:|
| discapacidad | Sí | 0.8863 | 4.24 | -3.3537 |

###### 5.3 Grupo étnico

| categoria | n | pct_base | pct_dane_2018 | brecha_pp |
|:---|---:|---:|---:|---:|
| NARP | 509 | 2.4923 | 9.34 | -6.8477 |
| Indígena | 114 | 0.5582 | 4.4 | -3.8418 |
| Rrom | 6 | 0.0294 | 0.006 | 0.0234 |

##### 6. Conclusión

La comparación se realizó mediante porcentajes y no por conteos absolutos, dado que la base de investigadores corresponde a una población específica y el DANE 2018 representa la población nacional. En consecuencia, las brechas se interpretan en puntos porcentuales.

---

## 4. Discusión integrada

Los cuatro ejes de análisis convergen en una imagen coherente del sistema colombiano de investigación reconocida:

**Eje longitudinal.** El sistema presenta inercia categorial elevada: la mayoría de los investigadores reconocidos mantienen su categoría entre convocatorias. Sin embargo, la comparación 2017→2019 versus 2019→2021 sugiere un cambio de tendencia: menor movilidad ascendente y mayor movilidad descendente, especialmente en la categoría Asociado. Una hipótesis plausible es que los requisitos de evaluación se hicieron más exigentes o que factores externos (pandemia, reducción de producción académica) afectaron el rendimiento medido.

**Eje territorial.** Con un HHI de 1 518 puntos, el sistema opera bajo concentración moderada pero estructuralmente robusta: los tres primeros departamentos explican más de la mitad del total. La concentración geográfica no es casual, sino el resultado acumulado de décadas de desigual inversión en educación superior y en infraestructura científica regional. El análisis de la red de co-filiación refuerza esta conclusión: las instituciones con mayor centralidad son precisamente las localizadas en los departamentos dominantes.

**Eje de redes.** La red de co-filiación es dispersa (densidad 0.06) y jerárquica (estructura de hub centrada en la UNAL). La co-filiación como práctica solo involucra al 1.15 % de los investigadores, lo que indica que la colaboración interinstitucional dentro del panel es todavía marginal. Esto sugiere tanto una oportunidad de política (incentivar la movilidad entre instituciones) como una limitación metodológica que debe señalarse: la variable `INST_FILIA` puede no capturar todas las formas de colaboración, en particular las formalizadas en proyectos sin co-autoría declarada en el formulario.

**Eje de diversidad.** Las brechas de representación documentadas en los tres indicadores (conflicto, etnia, discapacidad) son sistemáticas y estadísticamente relevantes. La comunidad investigadora reconocida no es un espejo de la sociedad colombiana en ninguna de estas dimensiones. Las brechas no son aleatorias: reflejan desigualdades estructurales reproducidas dentro del sistema científico. Este hallazgo es relevante para el diseño de políticas de inclusión y para los programas de becas y apoyos específicos que Minciencias puede implementar en futuras convocatorias.

---

## 5. Conclusiones

1. **Estabilidad con señales de tensión ascendente.** El sistema de categorización es estable pero muestra una ralentización de la movilidad ascendente y un incremento de los descensos en el periodo 2019→2021, especialmente en la categoría Asociado. El monitoreo longitudinal continuo es indispensable para distinguir si esta tendencia es transitoria o estructural.

2. **Concentración territorial moderada pero persistente.** Bogotá, Antioquia y Valle del Cauca concentran el 57 % de los investigadores únicos. Las regiones periféricas tienen participación marginal y no muestran señales de convergencia con los datos disponibles.

3. **Red de colaboración incipiente.** Sólo el 1.15 % de los investigadores declara co-filiación. La red resultante es baja en densidad y dominada por pocas instituciones de gran tradición. El fortalecimiento de la colaboración interinstitucional requiere incentivos explícitos en el modelo de evaluación.

4. **Brechas de diversidad sistemáticas.** Las poblaciones víctimas del conflicto (−9.7 pp), NARP (−6.8 pp), indígenas (−3.8 pp) y personas con discapacidad (−3.4 pp) están subrepresentadas en la comunidad investigadora respecto a la población general. Estas brechas son consistentes con las desigualdades estructurales del acceso a la educación superior en Colombia.

5. **Limitaciones de los datos.** Las variables de diversidad solo están disponibles para 2021, lo que impide análisis longitudinales de estas dimensiones. La convocatoria 2023 aún no ha sido publicada en el portal oficial, lo que restringe la extensión temporal del análisis.

---

## 6. Recomendaciones

- Incorporar las variables de diversidad (`ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO`, `TXT_POBLACION_DISCA`) en los formularios de convocatorias futuras para habilitar comparaciones temporales.
- Implementar políticas de focalización territorial que amplíen el acceso al reconocimiento en departamentos periféricos (Amazonia, Pacífico, Orinoquía).
- Diseñar incentivos de colaboración interinstitucional en los criterios de evaluación para incrementar la densidad de la red y reducir la dependencia del hub UNAL.
- Establecer estrategias de acción afirmativa dentro de las convocatorias para reducir las brechas de representación de poblaciones NARP, indígenas, víctimas del conflicto y personas con discapacidad.
- Actualizar el presente informe cuando la convocatoria 2023 sea publicada oficialmente para extender el análisis longitudinal.

---

## 7. Referencias

| Fuente | Descripción |
|:---|:---|
| Minciencias | Bases de datos de investigadores reconocidos — convocatorias 2017, 2019 y 2021. Portal datos.gov.co |
| DANE | Censo Nacional de Población y Vivienda 2018 — resultados de grupos étnicos, discapacidad y víctimas del conflicto |
| Newman, M. E. J. (2010) | *Networks: An Introduction*. Oxford University Press |
| Hirschman, A. O. (1964) | The paternity of an index. *American Economic Review*, 54(5), 761–762 |
| Minciencias | Modelo de medición de grupos e investigadores — bases conceptuales del sistema de categorización |

---

## 8. Archivos de respaldo en el repositorio

| Archivo | Contenido |
|:---|:---|
| `evidencias/evidencia_tarea1_tracking_longitudinal.md` | Detalle completo del análisis longitudinal y cuadros de movilidad |
| `evidencias/evidencia_tarea2_transiciones_categoria.md` | Matrices de transición observadas y probabilidades por categoría y periodo |
| `evidencias/matriz_transicion_2017_2019.csv` | Conteos de transición 2017→2019 |
| `evidencias/matriz_transicion_2019_2021.csv` | Conteos de transición 2019→2021 |
| `evidencias/matriz_probabilidades_2017_2019.csv` | Probabilidades de transición 2017→2019 |
| `evidencias/matriz_probabilidades_2019_2021.csv` | Probabilidades de transición 2019→2021 |
| `hallazgos/sprint_2_hhi_concentracion_territorial.md` | Concentración territorial HHI — metodología y resultados |
| `artifacts/sprint2_genero_ocde/tabla_pct_femenino_por_area_anio.csv` | Participación femenina por gran área OCDE, 2017–2021 |
| `hallazgos/sprint_3_cofiliacion_network.md` | Red de co-filiación — métricas y pares institucionales |
| `hallazgos/sprint_3_cofiliacion_nodes.csv` | Tabla de nodos del grafo institucional |
| `hallazgos/sprint_3_cofiliacion_edges.csv` | Tabla de aristas del grafo institucional |
| `hallazgos/sprint_3_cofiliacion_network.gexf` | Grafo exportado (Gephi / NetworkX) |
| `evidencias/sprint4/evidencia_sprint4_variables_dane_2018.md` | Análisis de diversidad 2021 y comparación con DANE 2018 (rama develop_mariap) |
