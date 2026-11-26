import pandas as pd


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """

    import glob
    from pathlib import Path

    lab_dir = Path(__file__).resolve().parents[1]
    files = sorted(glob.glob(str(lab_dir / "data" / "bank-marketing-campaing-*.csv.gz")))
    df = pd.concat(
        [pd.read_csv(path, compression="gzip") for path in files],
        ignore_index=True,
    )
    df["client_id"] = range(len(df))

    client = df[
        ["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]
    ].copy()
    client["job"] = client["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    client["education"] = client["education"].replace("unknown", pd.NA)
    client["education"] = client["education"].str.replace(".", "_", regex=False)
    client["credit_default"] = (client["credit_default"].str.lower() == "yes").astype(int)
    client["mortgage"] = (client["mortgage"].str.lower() == "yes").astype(int)

    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    campaign = df[
        [
            "client_id", "number_contacts", "contact_duration",
            "previous_campaign_contacts", "previous_outcome",
            "campaign_outcome", "month", "day",
        ]
    ].copy()
    campaign["previous_outcome"] = (campaign["previous_outcome"].str.lower() == "success").astype(int)
    campaign["campaign_outcome"] = (campaign["campaign_outcome"].str.lower() == "yes").astype(int)
    campaign["last_contact_date"] = (
        campaign["month"].str.lower().map(month_map).map(lambda month: f"{month:02d}")
    )
    campaign["last_contact_date"] = (
        "2022-" + campaign["last_contact_date"] + "-"
        + campaign["day"].astype(str).str.zfill(2)
    )
    campaign = campaign.drop(columns=["month", "day"])
    campaign = campaign[
        [
            "client_id", "number_contacts", "contact_duration",
            "previous_campaign_contacts", "previous_outcome",
            "campaign_outcome", "last_contact_date",
        ]
    ]

    economics = df[
        ["client_id", "cons_price_idx", "euribor_three_months"]
    ].copy()

    submission = lab_dir / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    client.to_csv(submission / "client.csv", index=False)
    campaign.to_csv(submission / "campaign.csv", index=False)
    economics.to_csv(submission / "economics.csv", index=False)
    return client, campaign, economics
