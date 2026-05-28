# Detalle comparativo de resultados

## 1) Objetivo
Comparar los resultados obtenidos en `notebooks/` y `notebooks_Minciencias/`, mostrando diferencias de enfoque, resultados cuantitativos y oportunidades de mejora.

---

## 2) Fuentes revisadas

### Notebooks base
- [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb)
- [notebooks/02_analisis_longitudinal.ipynb](notebooks/02_analisis_longitudinal.ipynb)

### Notebooks_Minciencias
- [notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/analisis_17.md](notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/analisis_17.md)
- [notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/2019_analisis.md](notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/2019_analisis.md)
- [notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/datos_2021.ipynb](notebooks_Minciencias/tarea_anlisis_bases_de_datos_Minciencias/datos_2021.ipynb)
- [notebooks_Minciencias/tarea_gran_tabla_Minciencias/analisis_Univariado.md](notebooks_Minciencias/tarea_gran_tabla_Minciencias/analisis_Univariado.md)
- [notebooks_Minciencias/tarea_gran_tabla_Minciencias/informe_multivariado.md](notebooks_Minciencias/tarea_gran_tabla_Minciencias/informe_multivariado.md)
- [notebooks_Minciencias/tarea_gran_tabla_Minciencias/informe_clusters.md](notebooks_Minciencias/tarea_gran_tabla_Minciencias/informe_clusters.md)

---

## 3) Comparación general

| Criterio | `notebooks/` | `notebooks_Minciencias/` |
|---|---|---|
| Enfoque | Exploratorio inicial | Análisis por tareas especializadas |
| Profundidad | Básica-intermedia | Intermedia-avanzada |
| Resultados | Conteos y gráficas base | Porcentajes, tablas, cruces y perfiles |
| Métodos | Descriptivos | Univariado, correspondencias, clústeres |

---

## 3.1) Comparativo anual por convocatoria (2017, 2019, 2021)

| Año | Registros | Hallazgos clave |
|---|---:|---|
| 2017 | 13.001 | Género: 62,6% hombres / 37,4% mujeres; Ciencias Sociales ~29%; concentración territorial en Bogotá y Eje Cafetero. |
| 2019 | 16.796 | Género: 61,83% hombres / 38,17% mujeres; Bogotá + Eje Cafetero > 60%. |
| 2021 | 21.094 | Género: 60,6% hombres / 39,3% mujeres; se mantiene centralización regional y alta formación de posgrado. |

El volumen crece de 2017 a 2021 y persisten patrones estructurales: brecha de género, concentración geográfica y predominio de posgrado.

---

## 4) Diferencias clave en resultados

- En `notebooks/` predominan resultados exploratorios rápidos, sin tablas comparativas anuales consolidadas.
- En `notebooks_Minciencias/` sí hay resultados cuantitativos reutilizables (porcentajes, tablas de frecuencias, cruces y perfiles).
- Se observa cobertura por año (2017, 2019 y 2021), permitiendo comparaciones de tendencia y consistencia de hallazgos.

---

## 5) Crítica constructiva

- **Crítica principal:** actualmente se usan varios lenguajes (Python y R), lo que fragmenta el flujo de trabajo.
- **Mejora propuesta:** estandarizar todo el pipeline en Python.
- **Beneficio esperado:** mayor reproducibilidad, menor complejidad operativa y resultados comparables en un solo formato.

---

## 6) Evidencias sugeridas para pantallazos

1. `notebooks/02_analisis_longitudinal.ipynb` → tendencia por convocatoria.
2. `analisis_17.md` → distribución por género 2017.
3. `2019_analisis.md` → tabla de región y porcentaje.
4. `datos_2021.ipynb` → resultados de género/edad/región en 2021.
5. `analisis_Univariado.md` → resumen estadístico y tablas de frecuencias.
6. `informe_multivariado.md` + `informe_clusters.md` → asociaciones y perfiles.

---

## 7) Conclusión
`notebooks` y `notebooks_Minciencias` se complementan, pero la capa de Minciencias aporta resultados más sólidos para decisión por su nivel de cuantificación. La prioridad técnica recomendada es migrar todo a Python para unificar ejecución y mantenimiento.