# Evidencia Issue 19 — Dashboard territorial

## Objetivo
Construir una vista territorial del número de investigadores reconocidos por MinCiencias
para las convocatorias 2017, 2019 y 2021, con apoyo de distribuciones por categoría y género.

## Implementación revisada
- Vista en `app/streamlit_app.py`
- Funciones de apoyo en `src/visualizacion/mapas.py`
- Filtro temporal con slider: 2017, 2019, 2021
- Gráficos incluidos:
  - mapa por departamento
  - distribución por categoría
  - distribución por género
  - tabla top 10 departamentos

## Fuente de datos
- Archivo: `datos/tarea_join/investigadores_consolidado.csv`
- Unidad de análisis: investigadores únicos (`ID_PERSONA_PR`)
- Variable territorial: `NME_DEPARTAMENTO_RES_PR`

## Resultados validados
- Investigadores únicos:
  - 2017: 13.001
  - 2019: 16.796
  - 2021: 21.094

- Top 5 departamentos en 2021:
  1. Bogotá, D. C. (6.582)
  2. Antioquia (3.528)
  3. Valle del Cauca (1.671)
  4. Atlántico (1.486)
  5. Santander (1.170)

## Consistencia interna
- Suma por categoría en 2021:
  - Junior: 13.370
  - Asociado: 4.601
  - Sénior: 3.040
  - Emérito: 83
  - Total: 21.094

- Suma por género en 2021:
  - Masculino: 12.787
  - Femenino: 8.298
  - Intersexual: 5
  - No disponible: 4
  - Total: 21.094

## Conclusión
El issue 19 queda cumplido porque permite comparar la evolución territorial entre 2017, 2019 y 2021
y muestra, además, la composición por categoría y género de forma consistente.