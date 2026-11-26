def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    from ._common import read_rows

    values = {}
    for letter, value, *_ in read_rows():
        number = int(value)
        if letter not in values:
            values[letter] = [number, number]
        else:
            values[letter][0] = max(values[letter][0], number)
            values[letter][1] = min(values[letter][1], number)
    return [(letter, bounds[0], bounds[1]) for letter, bounds in sorted(values.items())]
