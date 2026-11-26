def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    import re
    from pathlib import Path

    import pandas as pd

    lab_dir = Path(__file__).resolve().parents[1]
    df = pd.read_csv(
        lab_dir / "data" / "solicitudes_de_credito.csv.gz",
        compression="gzip",
        sep=";",
        encoding="cp1252",
    )
    df.columns = [
        "línea_credito" if str(column).strip().endswith("nea_credito") else str(column)
        for column in df.columns
    ]

    text_columns = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito",
    ]

    def clean_text(value):
        if pd.isna(value):
            return pd.NA
        value = str(value).lower().strip()
        import unicodedata
        value = "".join(
            character for character in unicodedata.normalize("NFD", value)
            if unicodedata.category(character) != "Mn"
        )
        if "organizaci" in value or "\ufffd" in value and "organizaci" in value:
            value = "organizacion y"
        if "pa" in value and "alera" in value:
            value = "panalera"
        value = re.sub(r"[_/-]+", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    for column in text_columns:
        df[column] = df[column].map(clean_text)

    df["comuna_ciudadano"] = pd.to_numeric(
        df["comuna_ciudadano"].astype(str).str.replace(r"\.0$", "", regex=True),
        errors="coerce",
    )
    df["estrato"] = pd.to_numeric(
        df["estrato"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
    ).astype("Int64")
    def clean_amount(value):
        if pd.isna(value):
            return pd.NA
        text = str(value).split(".", 1)[0]
        digits = re.sub(r"\D", "", text)
        return int(digits) if digits else pd.NA

    df["monto_del_credito"] = df["monto_del_credito"].map(clean_amount).astype("Int64")

    dates = pd.to_datetime(df["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce")
    dates = dates.fillna(pd.to_datetime(df["fecha_de_beneficio"], format="%Y-%m-%d", errors="coerce"))
    dates = dates.fillna(pd.to_datetime(df["fecha_de_beneficio"], format="%Y/%m/%d", errors="coerce"))
    df["fecha_de_beneficio"] = dates.dt.strftime("%Y-%m-%d")

    columns = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "estrato",
        "comuna_ciudadano", "fecha_de_beneficio", "monto_del_credito", "línea_credito",
    ]
    df = df[columns]
    df = df.dropna(subset=[column for column in columns if column != "comuna_ciudadano"])
    df = df.drop_duplicates()

    output = lab_dir / "submission" / "solicitudes_de_credito.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, sep=";", index=False)
