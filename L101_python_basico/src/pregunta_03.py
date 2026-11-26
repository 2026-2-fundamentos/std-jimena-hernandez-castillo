def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """

    from ._common import read_rows

    totals = {}
    for letter, value, *_ in read_rows():
        totals[letter] = totals.get(letter, 0) + int(value)
    return sorted(totals.items())
