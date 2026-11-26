def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """

    import pandas as pd
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    return pd.read_csv(path, sep="\t").shape[1]
