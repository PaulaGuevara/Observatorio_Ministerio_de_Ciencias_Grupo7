# Análisis de género por gran área OCDE
## Evolución de la brecha de género entre convocatorias 2017, 2019 y 2021

**Sprint 2 — Observatorio MinCiencias 2026-I**
**Autor:** Victor-Diaz-Usta
**Fecha:** 2026-03-21

---

## 1. Objetivo

Describir y cuantificar la evolución de la representación femenina en cada gran área del conocimiento (clasificación OCDE) a lo largo de las tres convocatorias de reconocimiento de investigadores de MinCiencias: 2017, 2019 y 2021.

---

## 2. Datos

- **Fuente:** `datos/tarea_join/investigadores_consolidado.csv`
- **Registros totales:** 50,891 (26,662 investigadores únicos)
- **Registros con género válido:** 50,882 (Masculino / Femenino)
- **Variables usadas:** `ANO_CONVO`, `NME_GRAN_AREA_PR`, `NME_GENERO_PR`
- **Grandes áreas OCDE identificadas:** 7

---

## 3. Resultados

### 3.1 Porcentaje de investigadoras mujeres por gran área y año

| Gran área OCDE | 2017 (%) | 2019 (%) | 2021 (%) | Cambio 2017→2021 (pp) |
|---|---:|---:|---:|---:|
| Ingeniería y Tecnología | 25.7 | 26.0 | 26.5 | +0.8 |
| Ciencias Agrícolas | 32.9 | 35.8 | 35.0 | +2.2 |
| Ciencias Naturales | 34.2 | 35.3 | 35.8 | +1.6 |
| Humanidades | 33.1 | 33.7 | 38.4 | +5.3 |
| Ciencias Sociales | 43.5 | 44.1 | 45.1 | +1.7 |
| Ciencias Médicas y de la Salud | 48.2 | 48.7 | 50.8 | +2.7 |

> La categoría "No registra" se excluye del análisis interpretativo por inconsistencia en los datos (0% en 2017 por ausencia de registros, no por ausencia real de mujeres).

### 3.2 Visualizaciones generadas

| Figura | Descripción | Archivo |
|---|---|---|
| Fig. 1 | Barras agrupadas: % mujeres por área y año | `fig1_barras_pct_femenino.png` |
| Fig. 2 | Heatmap: % mujeres por área y año | `fig2_heatmap_pct_femenino.png` |
| Fig. 3 | Líneas: evolución temporal por área | `fig3_lineas_evolucion.png` |
| Fig. 4 | Brecha de género (% masc − % fem) por área | `fig4_brecha_genero.png` |

---

## 4. Hallazgos principales

### Ingeniería y Tecnología: la brecha más amplia y persistente
Con apenas un 25.7% de mujeres en 2017 y 26.5% en 2021, esta área presenta la mayor segregación de género. El avance en cuatro años es de menos de **1 punto porcentual**, lo que indica que la brecha estructural no está cerrando a un ritmo significativo.

### Ciencias Médicas y de la Salud: la única área con paridad
Es el único campo que alcanzó la paridad de género en 2021 (50.8% mujeres), superando por primera vez el umbral del 50%. Ya en 2017 estaba muy próximo (48.2%), lo que refleja una tendencia histórica de mayor participación femenina en estas disciplinas.

### Humanidades: el avance más significativo
Con un incremento de **5.3 puntos porcentuales** (de 33.1% a 38.4%), Humanidades registra el mayor progreso de las áreas con datos consistentes en los tres años. Aunque aún lejos de la paridad, la tendencia es claramente positiva.

### Ciencias Sociales: cercanas a la paridad
Con 45.1% de mujeres en 2021, las Ciencias Sociales son el área con mayor representación femenina después de Salud, y muestran una evolución estable (+1.7 pp).

### Patrón transversal: el cambio es lento
El promedio de avance entre 2017 y 2021 en todas las áreas es de aproximadamente **2 puntos porcentuales**, lo que sugiere que, a este ritmo, la paridad en áreas como Ingeniería tardaría más de **90 años** en alcanzarse.

---

## 5. Conclusiones

1. **La segregación de género por área del conocimiento es estructural y persistente.** Las brechas observadas en 2017 se mantienen prácticamente intactas en 2021.
2. **Ingeniería y Tecnología concentra la mayor desigualdad** con una brecha de ~47 puntos porcentuales (73.5% masculino vs 26.5% femenino en 2021).
3. **Solo Ciencias Médicas y de la Salud ha alcanzado la paridad**, siendo la excepción dentro del sistema.
4. **El ritmo de cambio es insuficiente** para responder a la pregunta de investigación sobre si la representación femenina ha mejorado *significativamente* entre 2017 y 2021: el avance existe pero es marginal en la mayoría de áreas.

---

## 6. Artefactos generados

- `artifacts/sprint2_genero_ocde/fig1_barras_pct_femenino.png`
- `artifacts/sprint2_genero_ocde/fig2_heatmap_pct_femenino.png`
- `artifacts/sprint2_genero_ocde/fig3_lineas_evolucion.png`
- `artifacts/sprint2_genero_ocde/fig4_brecha_genero.png`
- `artifacts/sprint2_genero_ocde/tabla_pct_femenino_por_area_anio.csv`
- `notebooks/sprint2_genero_ocde/analisis_genero_ocde.py`
