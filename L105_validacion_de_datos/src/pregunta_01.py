def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    import json
    import re
    from pathlib import Path

    import pandas as pd

    lab_dir = Path(__file__).resolve().parents[1]
    path = lab_dir / "data" / "ventas.csv.gz"
    df = pd.read_csv(path, compression="gzip", dtype=str)
    df.columns = [
        re.sub(r"\s+", "_", str(column).lower().strip().lstrip("\ufeff"))
        for column in df.columns
    ]
    required = [
        "supplier_id", "supplier", "country", "city", "purchase_date",
        "amount", "discount", "weight", "units", "unit_price", "contact_email",
    ]
    missing_required = sorted(set(required) - set(df.columns))
    unexpected = sorted(set(df.columns) - set(required))

    missing_mask = df.isna() | df.apply(
        lambda column: column.astype(str).str.strip().isin(["", "N/A"])
    )
    missing_by_column = {
        column: int(missing_mask[column].sum())
        for column in df.columns
    }

    supplier_ids = df["supplier_id"] if "supplier_id" in df else pd.Series(dtype=str)
    supplier_counts = supplier_ids.value_counts(dropna=False)
    duplicate_supplier_count = int(
        supplier_ids.isin(supplier_counts[supplier_counts > 1].index).sum()
    )

    emails = df["contact_email"] if "contact_email" in df else pd.Series(dtype=str)
    email_valid = emails.astype(str).str.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+")
    invalid_email_count = int((~email_valid.fillna(False) & emails.notna()).sum())

    units = df["units"] if "units" in df else pd.Series(dtype=str)
    numeric_units = pd.to_numeric(units, errors="coerce")
    invalid_units = units.notna() & ~units.astype(str).str.strip().isin(["", "N/A"]) & (
        numeric_units.isna() | (numeric_units <= 0) | (numeric_units % 1 != 0)
    )

    report = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_required_columns": missing_required,
        "unexpected_columns": unexpected,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": duplicate_supplier_count,
        "missing_value_count_by_column": missing_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": int(invalid_units.sum()),
        "country_values": sorted(df["country"].dropna().astype(str).unique())
        if "country" in df else [],
    }
    output = lab_dir / "submission" / "data_quality_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
