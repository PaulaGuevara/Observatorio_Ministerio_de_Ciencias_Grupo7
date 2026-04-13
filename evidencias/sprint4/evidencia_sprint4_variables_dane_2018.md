# Evidencia Sprint 4

## 1. Fuente de entrada

- Archivo analizado: `datos/tarea_join/investigadores_consolidado.csv`
- Año seleccionado para la explotación: **2021**

## 2. Disponibilidad de variables por año

Se revisaron las convocatorias disponibles y se verificó la disponibilidad de `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO` y `TXT_POBLACION_DISCA`.

|   anio |   n_registros |   ID_VICTIMA_CONFLICTO_n_util |   ID_VICTIMA_CONFLICTO_pct_util |   TXT_GRUPO_ETNICO_n_util |   TXT_GRUPO_ETNICO_pct_util |   TXT_POBLACION_DISCA_n_util |   TXT_POBLACION_DISCA_pct_util |
|-------:|--------------:|------------------------------:|--------------------------------:|--------------------------:|----------------------------:|-----------------------------:|-------------------------------:|
|   2017 |         13001 |                             0 |                            0    |                         0 |                        0    |                            0 |                           0    |
|   2019 |         16796 |                             0 |                            0    |                         0 |                        0    |                            0 |                           0    |
|   2021 |         21094 |                         20423 |                           96.82 |                     20423 |                       96.82 |                        20421 |                          96.81 |

## 3. Justificación metodológica

Aunque el proyecto trabaja con 2017, 2019 y 2021, la explotación sustantiva de estas variables se realiza sobre el año con información útil. Si en un año los registros aparecen únicamente como `No registra` o `No disponible`, ese año se documenta, pero no se usa para calcular porcentajes comparables con DANE.

## 4. Resultados descriptivos

### 4.1 Víctima del conflicto

| categoria   |     n |   pct_total |   pct_validos |
|:------------|------:|------------:|--------------:|
| No          | 20002 |     94.8232 |       97.9386 |
| No informa  |   671 |      3.181  |        0      |
| Sí          |   421 |      1.9958 |        2.0614 |

### 4.2 Grupo étnico

| categoria           |     n |   pct_total |   pct_validos |
|:--------------------|------:|------------:|--------------:|
| Ningún grupo étnico | 19674 |     93.2682 |       96.3326 |
| No informa          |   671 |      3.181  |        0      |
| NARP                |   509 |      2.413  |        2.4923 |
| Blanco o mestizo    |   120 |      0.5689 |        0.5876 |
| Indígena            |   114 |      0.5404 |        0.5582 |
| Rrom                |     6 |      0.0284 |        0.0294 |

### 4.3 Discapacidad (detalle)

| categoria   |     n |   pct_total |   pct_validos |
|:------------|------:|------------:|--------------:|
| Ninguna     | 20240 |     95.9515 |       99.1137 |
| No informa  |   673 |      3.1905 |        0      |
| Visual      |    68 |      0.3224 |        0.333  |
| Física      |    55 |      0.2607 |        0.2693 |
| Auditiva    |    42 |      0.1991 |        0.2057 |
| Psicosocial |     6 |      0.0284 |        0.0294 |
| Intelectual |     6 |      0.0284 |        0.0294 |
| Múltiple    |     4 |      0.019  |        0.0196 |

### 4.4 Discapacidad (binaria)

| categoria   |     n |   pct_total |   pct_validos |
|:------------|------:|------------:|--------------:|
| No          | 20240 |     95.9515 |       99.1137 |
| No informa  |   673 |      3.1905 |        0      |
| Sí          |   181 |      0.8581 |        0.8863 |

## 5. Comparación con DANE 2018

### 5.1 Víctima del conflicto

| indicador             | categoria   |   pct_base |   pct_dane_2018 |   brecha_pp |
|:----------------------|:------------|-----------:|----------------:|------------:|
| víctima del conflicto | Sí          |     2.0614 |            11.8 |     -9.7386 |

### 5.2 Discapacidad

| indicador    | categoria   |   pct_base |   pct_dane_2018 |   brecha_pp |
|:-------------|:------------|-----------:|----------------:|------------:|
| discapacidad | Sí          |     0.8863 |            4.24 |     -3.3537 |

### 5.3 Grupo étnico

| categoria   |   n |   pct_base |   pct_dane_2018 |   brecha_pp |
|:------------|----:|-----------:|----------------:|------------:|
| NARP        | 509 |     2.4923 |           9.34  |     -6.8477 |
| Indígena    | 114 |     0.5582 |           4.4   |     -3.8418 |
| Rrom        |   6 |     0.0294 |           0.006 |      0.0234 |

## 6. Conclusión

La comparación se realizó mediante porcentajes y no por conteos absolutos, dado que la base de investigadores corresponde a una población específica y el DANE 2018 representa la población nacional. En consecuencia, las brechas se interpretan en puntos porcentuales.
