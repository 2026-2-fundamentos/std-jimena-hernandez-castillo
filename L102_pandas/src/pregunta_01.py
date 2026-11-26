def pregunta_01():
    """
    ¿Cuántos registros tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        40
    """

    import pandas as pd
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    return len(pd.read_csv(path, sep="\t"))
