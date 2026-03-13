# datos/raw/

Este directorio almacena los archivos CSV descargados desde el portal de
Datos Abiertos de Colombia por el script `src/ingesta/minciencias.py`.

Los archivos generados tienen la forma:

```
investigadores_reconocidos_2017.csv
investigadores_reconocidos_2019.csv
investigadores_reconocidos_2021.csv
```

> **Nota:** Los archivos CSV están excluidos del control de versiones
> (ver `.gitignore`). Para reproducir la descarga ejecuta:
>
> ```bash
> pip install -r requirements.txt
> python -m src.ingesta.minciencias
> ```
