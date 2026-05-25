# Evidencia Issue 20 — Ranking de instituciones

## Objetivo
Construir un ranking de instituciones por número de investigadores reconocidos,
con filtros por categoría y área del conocimiento.

## Implementación revisada
- Vista en `app/streamlit_app.py`
- Funciones de apoyo en `src/visualizacion/instituciones.py`
- Filtros disponibles:
  - categoría
  - área
  - top N

## Fuente de datos
- Archivo: `datos/tarea_join/investigadores_consolidado.csv`
- Unidad de análisis: investigadores únicos (`ID_PERSONA_PR`)
- Variable de institución: `INST_FILIA`

## Regla metodológica
Cuando un investigador tiene varias instituciones en `INST_FILIA`, la cadena se divide por `|`
y luego se expande a una fila por institución. Después se eliminan duplicados por
investigador + institución + año.

## Resultados validados
### Ranking general 2021
1. Universidad de Antioquia — 787
2. Universidad Nacional sede Bogotá — 629
3. Pontificia Universidad Javeriana — 526
4. Universidad del Valle — 427
5. Universidad de los Andes — 406

### Liderazgo por categoría
- Junior: Universidad de Antioquia — 457
- Asociado: Pontificia Universidad Javeriana / Nacional sede Bogotá — 140
- Sénior: Nacional sede Bogotá — 239
- Emérito: Nacional sede Bogotá / Nacional sede Medellín — 8

### Liderazgo por gran área
- Ciencias Agrícolas: Agrosavia — 137
- Ciencias Médicas y de la Salud: Universidad de Antioquia — 202
- Ciencias Naturales: Nacional sede Bogotá — 211
- Ciencias Sociales: Universidad de Antioquia — 171
- Humanidades: Pontificia Universidad Javeriana — 66
- Ingeniería y Tecnología: Universidad de Antioquia — 131


## Conclusión
El issue 20 queda cumplido porque el dashboard permite construir el ranking institucional
y refinarlo por categoría y área, mostrando cambios en el liderazgo según el criterio elegido.