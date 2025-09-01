# Análisis base de datos 2017

La base de datos contiene 13.001 registros y 30 variables, correspondientes a investigadores reconocidos en convocatorias.

## Descripción general:

Convocatorias: Identifica la convocatoria (ID_CONVOCATORIA, NME_CONVOCATORIA, ANO_CONVO).

Investigador: Incluye un identificador único (ID_PERSONA_PR) y variables sociodemográficas (género, edad, país y lugar de nacimiento, lugar de residencia, etnia, condición de víctima del conflicto, discapacidad).

Área de conocimiento: Se especifica el área específica (NME_ESP_AREA_PR), el área general (NME_AREA_PR) y el gran campo disciplinar (NME_GRAN_AREA_PR).

Formación académica: Nivel de formación (NME_NIV_FORM_PR), orden en el que se registra.

Clasificación del investigador: Nivel de reconocimiento (NME_CLASIFICACION_PR).

Ubicación geográfica: País, región, departamento y municipio de residencia.

Afiliación institucional: Nombre de la institución (INST_FILIA).

## Gráficas e interpretaciones

### Variables no útililes para la vizualización

En el proceso de análisis y visualización de la base de datos de investigadores reconocidos por convocatoria, se identificaron algunas variables que no resultan relevantes para la construcción de gráficos ni para la interpretación de tendencias. Estas variables corresponden principalmente a identificadores internos (como códigos únicos de personas, convocatorias), que cumplen una función técnica en la gestión de datos, pero que no aportan información de valor para representar visualmente la población.


Asimismo, existen campos que resultan redundantes o poco informativos: por ejemplo, códigos geográficos (COD_DANE_NAC_PR, COD_DANE_RES_PR) que ya están representados de manera más comprensible mediante nombres de municipios, departamentos o regiones

En consecuencia, para lograr visualizaciones más claras, comprensibles y orientadas al análisis de características sociodemográficas, geográficas y académicas de los investigadores, se decidió excluir las siguientes variables:

#### Identificadores

ID_CONVOCATORIA

ID_PERSONA_PR

ID_AREA_CON_PR

ID_NIV_FORMACION_PR

ID_CLAS_PR

ID_VICTIMA_CONFLICTO

#### Variables redundantes / técnicas

NME_CONVOCATORIA

ANO_CONVO

NRO_ORDEN_FORM_PR

ORDEN_CLAS_PR

COD_DANE_NAC_PR

COD_DANE_RES_PR

### Análisis útililes para la vizualización


Variables no útililes para la vizualización
