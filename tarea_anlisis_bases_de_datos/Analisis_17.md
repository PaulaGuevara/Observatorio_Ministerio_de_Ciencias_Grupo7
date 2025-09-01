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

Se hara un corto análisis de faltantes

<img width="1438" height="841" alt="Captura de pantalla 2025-09-01 a la(s) 3 57 41 p m" src="https://github.com/user-attachments/assets/581d1afa-6cd6-4fe7-a84c-f86f83c86a2b" />


Se observa que hay tres variables con faltantes, las cuales dos son los coidgos del Dane, con el 2.24% y 6.08%, ahora esto se debe a que el investigador esta en el exterior o no esta disponible la información, no es un problema de faltantes para la base. La tercera variable con el 12.57% es la variable INST_FIlA, si el investigador no tiene filación con ninguna isntitución no se tomara el dato y quedara como dato faltante por lo que no es un problema para la base.


#### NME_ESP_AREA_PR: Especialidad del área de conocimiento OCDE principal del investigador



<img width="1440" height="900" alt="Captura de pantalla 2025-09-01 a la(s) 6 12 20 p m" src="https://github.com/user-attachments/assets/0d36ec5b-4f53-44b3-9727-8f34c3db1469" />












