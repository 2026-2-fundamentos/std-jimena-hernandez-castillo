def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    import json
    from pathlib import Path

    import pandas as pd

    lab_dir = Path(__file__).resolve().parents[1]
    df = pd.read_csv(lab_dir / "data" / "insurance.csv.gz", compression="gzip")

    def age_group(age):
        if age < 30:
            return "18-29"
        if age < 40:
            return "30-39"
        if age < 50:
            return "40-49"
        return "50-64"

    def bmi_group(bmi):
        if bmi < 18.5:
            return "bajo peso"
        if bmi < 25:
            return "normal"
        if bmi < 30:
            return "sobrepeso"
        return "obesidad"

    def children_group(children):
        if children == 0:
            return "0"
        if children <= 2:
            return "1-2"
        return "3+"

    df["age_group"] = df["age"].map(age_group)
    df["bmi_group"] = df["bmi"].map(bmi_group)
    df["children_group"] = df["children"].map(children_group)

    original_quasi = ["age", "sex", "bmi", "children", "region"]
    original_sizes = df.groupby(original_quasi, dropna=False).size()
    original_k = int(original_sizes.min())
    original_unique = int((original_sizes == 1).sum())

    schemes = {}
    published_frames = {}
    for name, quasi in (
        ("with_children", ["age_group", "sex", "bmi_group", "children_group", "region"]),
        ("without_children", ["age_group", "sex", "bmi_group", "region"]),
    ):
        generalized = df.copy()
        sizes = generalized.groupby(quasi, dropna=False).size()
        published_mask = generalized.set_index(quasi).index.map(sizes)
        published = generalized[published_mask >= 5].copy()
        published_classes = published.groupby(quasi, dropna=False).size()
        diversity = published.groupby(quasi)["smoker"].nunique()
        nondiverse_classes = int((diversity == 1).sum())
        nondiverse_records = int(
            published.set_index(quasi).index.isin(diversity[diversity == 1].index).sum()
        )
        schemes[name] = {
            "quasi_identifiers": quasi,
            "equivalence_classes": int(sizes.shape[0]),
            "k_before_suppression": int(sizes.min()),
            "suppressed_records": int(len(df) - len(published)),
            "published_records": int(len(published)),
            "published_classes": int(published_classes.shape[0]),
            "classes_without_smoker_diversity": nondiverse_classes,
            "records_without_smoker_diversity": nondiverse_records,
        }
        published_frames[name] = published

    selected = min(schemes, key=lambda name: schemes[name]["suppressed_records"])
    published = published_frames[selected]
    published_columns = schemes[selected]["quasi_identifiers"] + ["smoker", "charges"]
    published_output = published[published_columns]

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique,
        "schemes": schemes,
        "selected_scheme": selected,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(published["charges"].mean()),
        "smoker_rate_original": float((df["smoker"] == "yes").mean()),
        "smoker_rate_published": float((published["smoker"] == "yes").mean()),
    }
    submission = lab_dir / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    (submission / "privacy_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    published_output.to_csv(submission / "insurance_published.csv", index=False)
    return report
