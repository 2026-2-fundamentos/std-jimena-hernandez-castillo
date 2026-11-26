def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """

    from ._common import read_rows, split_codes

    totals = {}
    for row in read_rows():
        value = int(row[1])
        for code in set(split_codes(row[3])):
            totals[code] = totals.get(code, 0) + value
    return dict(sorted(totals.items()))
