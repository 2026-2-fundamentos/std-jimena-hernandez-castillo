def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """

    from collections import Counter

    from ._common import read_rows, split_metrics

    counts = Counter(key for row in read_rows() for key, _ in split_metrics(row[4]))
    return dict(sorted(counts.items()))
