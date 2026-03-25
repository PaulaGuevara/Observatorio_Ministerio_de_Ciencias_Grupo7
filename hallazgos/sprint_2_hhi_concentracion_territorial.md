# Sprint 2 - Indice Herfindahl-Hirschman por departamento

## Objetivo

Medir qué tan concentrada está la investigación reconocida por Minciencias en los departamentos de residencia, con énfasis en Bogotá, Antioquia y Valle del Cauca.

## Fuente y criterio metodológico

- Fuente base: `datos/tarea_join/investigadores_consolidado.csv`.
- Variable de análisis: `NME_DEPARTAMENTO_RES_PR`.
- Resultado principal: base depurada por persona única, conservando la convocatoria más reciente por `ID_PERSONA_PR`, de acuerdo con el criterio documentado en `notebooks_Minciencias/tarea_tabla_Minciencias/README.md`.
- Resultado comparativo: consolidado completo 2017-2019-2021 sin deduplicación.

## Fórmula usada

El índice Herfindahl-Hirschman se calculó como:

$$
HHI = \sum_{i=1}^n s_i^2
$$

donde $s_i$ es la participación de cada departamento sobre el total de investigadores. También se reporta el índice en escala tradicional de 0 a 10.000:

$$
HHI_{10000} = HHI \times 10000
$$

## Resultado principal: base depurada por persona única

- Total de investigadores únicos: 26.662
- Número de departamentos/categorías observadas: 35
- HHI: 0.1518
- HHI (0 a 10.000): 1517.56
- Nivel de concentración: **moderada**

Interpretación: el sistema de investigación reconocido presenta una **concentración territorial moderada**, con un peso especialmente fuerte en Bogotá, Antioquia y Valle del Cauca.

### Bogotá, Antioquia y Valle del Cauca

| Departamento | Investigadores | Participación |
|---|---:|---:|
| Bogotá, D. C. | 8.612 | 32.30% |
| Antioquia | 4.425 | 16.60% |
| Valle del Cauca | 2.197 | 8.24% |

En conjunto, estos tres territorios concentran **57.14%** de los investigadores únicos reconocidos.

### Top 10 departamentos de residencia

| Departamento | Investigadores | Participación |
|---|---:|---:|
| Bogotá, D. C. | 8.612 | 32.30% |
| Antioquia | 4.425 | 16.60% |
| Valle del Cauca | 2.197 | 8.24% |
| Atlántico | 1.778 | 6.67% |
| Santander | 1.412 | 5.30% |
| Caldas | 775 | 2.91% |
| Exterior | 767 | 2.88% |
| Boyacá | 711 | 2.67% |
| Bolívar | 698 | 2.62% |
| Norte de Santander | 615 | 2.31% |

Los cinco primeros departamentos concentran **69.10%** del total.

### Departamentos con menor participación

| Departamento | Investigadores | Participación |
|---|---:|---:|
| Vichada | 1 | 0.00% |
| Guaviare | 2 | 0.01% |
| Vaupés | 2 | 0.01% |
| Putumayo | 3 | 0.01% |
| Guainía | 5 | 0.02% |

## Resultado comparativo: consolidado completo sin deduplicar

- Total de registros: 50.891
- HHI: 0.1532
- HHI (0 a 10.000): 1531.88
- Nivel de concentración: **moderada**
- Participación conjunta de Bogotá, Antioquia y Valle del Cauca: **57.53%**

Este contraste muestra que la deduplicación por persona no altera de forma sustantiva la conclusión: la concentración territorial se mantiene en un rango **moderado** y sigue dominada por los mismos tres departamentos.

## Respuesta directa a la pregunta del profesor

Sí, la investigación reconocida está fuertemente concentrada en **Bogotá, Antioquia y Valle del Cauca**.

- En la base depurada, estos tres departamentos reúnen **57.14%** de los investigadores.
- Bogotá por sí sola concentra **32.30%**.
- Antioquia aporta **16.60%**.
- Valle del Cauca aporta **8.24%**.

Aunque el HHI no ubica el sistema en un nivel extremo de monopolización territorial, sí evidencia una estructura centralizada alrededor de pocos polos científicos, especialmente el eje **Bogotá-Antioquia-Valle del Cauca**.

## Conclusiones

1. El HHI territorial para investigadores únicos es **1517.56**, lo que indica una concentración **moderada**.
2. Bogotá es el principal nodo territorial de la investigación reconocida en Colombia.
3. Antioquia y Valle del Cauca consolidan, junto con Bogotá, el núcleo dominante del sistema.
4. La concentración territorial es robusta al criterio de deduplicación.
5. El resultado es robusto: al comparar base deduplicada y consolidado total, la lectura sustantiva no cambia.
