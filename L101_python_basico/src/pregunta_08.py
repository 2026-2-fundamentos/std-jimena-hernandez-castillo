def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    from ._common import read_rows

    letters_by_value = {}
    for letter, value, *_ in read_rows():
        letters_by_value.setdefault(int(value), set()).add(letter)
    return [(value, sorted(letters_by_value[value])) for value in sorted(letters_by_value)]
