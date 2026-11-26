def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """

    from ._common import read_rows

    letters_by_value = {}
    for letter, value, *_ in read_rows():
        letters_by_value.setdefault(int(value), []).append(letter)
    return [(value, letters_by_value[value]) for value in sorted(letters_by_value)]
