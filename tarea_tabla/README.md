##Depuración de IDs duplicados por convocatoria

Durante el proceso de limpieza de la base de datos se detectó la presencia de registros repetidos por persona en distintas convocatorias.
Para asegurar la consistencia del dataset y mantener únicamente la información más reciente de cada persona, se definió la siguiente regla de depuración:

Si un mismo ID aparecía en más de una convocatoria (por ejemplo, 19, 20 y 21), se conservó únicamente el registro correspondiente a la convocatoria más alta (más reciente).

Los registros asociados a convocatorias anteriores fueron eliminados.

Después de aplicar este procedimiento, el dataset final quedó conformado por 26.662 registros, garantizando que para cada persona solo se conserve la versión más actualizada de su información.
