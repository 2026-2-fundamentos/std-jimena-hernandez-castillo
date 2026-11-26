def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """

    from ._common import read_rows, split_metrics

    bounds = {}
    for row in read_rows():
        for key, value in split_metrics(row[4]):
            if key not in bounds:
                bounds[key] = [value, value]
            else:
                bounds[key][0] = min(bounds[key][0], value)
                bounds[key][1] = max(bounds[key][1], value)
    return [(key, minimum, maximum) for key, (minimum, maximum) in sorted(bounds.items())]
