# Sprint 3 - Network analysis de co-filiación

## Objetivo

Construir un grafo institucional de co-filiación usando `INST_FILIA` (separado por `|`), donde:

- Nodos: instituciones.
- Aristas: pares de instituciones conectadas por investigadores compartidos.
- Peso de arista: número de investigadores que comparten ambas instituciones.

## Configuración del modelo

- Fuente: `datos/tarea_join/investigadores_consolidado.csv`
- Umbral mínimo de investigadores compartidos por arista: **2**
- Se normalizaron variantes institucionales (sedes, paréntesis y formatos de escritura) para reducir duplicados nominales.

## Métricas generales del grafo

- Investigadores con al menos una afiliación: **46618**
- Investigadores con co-filiación (>=2 instituciones): **537**
- Porcentaje con co-filiación: **1.15%**
- Instituciones (nodos activos): **31**
- Conexiones de co-filiación (aristas): **28**
- Componentes conectados: **4**
- Densidad de red: **0.060215**

## Instituciones más conectadas

| Institución | Investigadores afiliados | Peso de conexión | Centralidad de grado |
|---|---:|---:|---:|
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | 3453 | 28 | 0.3667 |
| UNIVERSIDAD DE ANTIOQUIA | 2238 | 19 | 0.2667 |
| PONTIFICIA UNIVERSIDAD JAVERIANA | 1825 | 8 | 0.1333 |
| UNIVERSIDAD DE LOS ANDES | 1175 | 5 | 0.0667 |
| UNIVERSIDAD EAFIT | 562 | 4 | 0.0667 |
| UNIVERSIDAD DE SAN BUENAVENTURA CALI (UNIVERSIDAD DE SAN BUENAVENTURA) | 552 | 4 | 0.0667 |
| UNIVERSIDAD DE MEDELLIN | 391 | 4 | 0.0667 |
| INSTITUTO TECNOLOGICO METROPOLITANO DE MEDELLIN | 299 | 4 | 0.0667 |
| UNIVERSIDAD INDUSTRIAL DE SANTANDER | 915 | 3 | 0.0333 |
| FUNDACION UNIVERSIDAD DEL NORTE | 738 | 3 | 0.0333 |
| COLEGIO MAYOR NUESTRA SENORA DEL ROSARIO | 633 | 3 | 0.0333 |
| UNIVERSIDAD DEL ROSARIO (COLEGIO MAYOR NUESTRA SENORA DEL ROSARIO) | 72 | 3 | 0.0333 |

## Pares institucionales con mayor co-filiación

| Institución A | Institución B | Investigadores compartidos |
|---|---|---:|
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD DE ANTIOQUIA | 5 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD INDUSTRIAL DE SANTANDER | 3 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD DE LOS ANDES | 3 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | FUNDACION UNIVERSIDAD DEL NORTE | 3 |
| COLEGIO MAYOR NUESTRA SENORA DEL ROSARIO | UNIVERSIDAD DEL ROSARIO (COLEGIO MAYOR NUESTRA SENORA DEL ROSARIO) | 3 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD DISTRITAL FRANCISCO JOSE DE CALDAS | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD DE LOS LLANOS | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | UNIVERSIDAD CENTRAL | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | INSTITUTO TECNOLOGICO METROPOLITANO DE MEDELLIN | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | INSTITUTO NACIONAL DE SALUD | 2 |
| UNIVERSIDAD NACIONAL DE COLOMBIA SEDE BOGOTA (UNIVERSIDAD NACIONAL DE COLOMBIA) | INSTITUTO DE INVESTIGACION DE RECURSOS BIOLOGICOS ALEXANDER VON HUMBOLDT | 2 |
| UNIVERSIDAD EL BOSQUE | PONTIFICIA UNIVERSIDAD JAVERIANA | 2 |
| UNIVERSIDAD DEL VALLE | UNIVERSIDAD DE CARTAGENA | 2 |
| UNIVERSIDAD DE SAN BUENAVENTURA CALI (UNIVERSIDAD DE SAN BUENAVENTURA) | UNIVERSIDAD CATOLICA LUIS AMIGO | 2 |

## Entregables

- `hallazgos/sprint_3_cofiliacion_network.md`: reporte del Sprint 3.
- `hallazgos/sprint_3_cofiliacion_nodes.csv`: tabla de nodos.
- `hallazgos/sprint_3_cofiliacion_edges.csv`: tabla de aristas.
- `hallazgos/sprint_3_cofiliacion_network.gexf`: grafo exportado desde NetworkX.
