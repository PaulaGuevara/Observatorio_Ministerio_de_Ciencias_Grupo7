# Organizacion del Repositorio (Estilo Marie Kondo)

Objetivo: mantener claridad sin perder historial ni evidencia del trabajo.

## Principios

1. Conservar: no se elimina material academico ni evidencia valida.
2. Agrupar por funcion: datos, codigo, evidencia, hallazgos, documentacion.
3. Nombrar con intencion: prefijos por sprint o tema para facilitar busqueda.
4. Trazabilidad primero: todo entregable debe apuntar a su fuente y evidencia.

## Mapa oficial de uso

- [datos/](../datos): entrada, catalogos y datasets consolidados.
- [src/](../src): codigo reusable para ingesta, transformacion y visualizacion.
- [notebooks/](../notebooks): notebooks operativos del proyecto.
- [notebooks_Minciencias/](../notebooks_Minciencias): historico de tareas por componente.
- [hallazgos/](../hallazgos): entregables finales para mostrar y evidencias de soporte (HTML/MD/CSV/GEXF).
- [docs/](../docs): documentacion final y guias de organizacion.

## Reglas practicas para la rama develop

1. No mezclar en un mismo commit cambios de datos + cambios de codigo + cambios de redaccion.
2. Si se crea un archivo nuevo, actualizar indice correspondiente:
   - [README.md](../README.md)
   - [hallazgos/README.md](../hallazgos/README.md)
3. Mantener nombres con prefijo consistente:
   - sprint_2_...
   - sprint_3_...
   - sprint_4_...
4. Evitar duplicidad funcional:
   - si existen variantes de dashboard, documentar cual es principal.
   - si existen catalogos multiples, declarar uno como referencia principal.
5. Todo archivo pesado o generado automaticamente debe quedar en carpeta semantica (artifacts, hallazgos o evidencias), no en raiz.

## Ruta sugerida para validacion del profesor

1. Contexto general: [README.md](../README.md)
2. Entregables visuales: [hallazgos/README.md](../hallazgos/README.md)
3. Evidencia trazable: [hallazgos/evidencias/](../hallazgos/evidencias)
4. Informe final: [docs/sprint_4_informe_final.md](sprint_4_informe_final.md)

## Estado actual de orden

- La documentacion principal refleja la estructura real del repositorio.
- Hallazgos tiene indice propio con archivos listados por finalidad.
- No se eliminaron archivos ni se alteraron datasets.
