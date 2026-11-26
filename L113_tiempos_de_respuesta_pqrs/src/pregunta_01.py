import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    import numpy as np
    from pathlib import Path

    lab_dir = Path(__file__).resolve().parents[1]
    frames = []
    for channel in ("letter", "web"):
        df = pd.read_csv(
            lab_dir / "data" / f"historical_requests_{channel}.csv.gz",
            compression="gzip",
        )
        df = df.drop_duplicates()
        df["channel"] = channel
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["in_date"] = pd.to_datetime(df["in_date"], errors="coerce")
    df["out_date"] = pd.to_datetime(df["out_date"], errors="coerce")
    answered = df["out_date"].notna()
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days
    df["business_days"] = [
        int(pd.bdate_range(start + pd.Timedelta(days=1), end).size)
        if pd.notna(start) and pd.notna(end)
        else np.nan
        for start, end in zip(df["in_date"], df["out_date"])
    ]
    df["on_time"] = answered & (df["business_days"] <= 15)

    def summarize(group):
        answered_group = group["out_date"].notna()
        return pd.Series({
            "requests": len(group),
            "answered": int(answered_group.sum()),
            "pending": int((~answered_group).sum()),
            "median_business_days": group.loc[answered_group, "business_days"].median(),
            "on_time_rate": group["on_time"].mean(),
        })

    channel_summary = (
        df.groupby("channel", sort=True)
        .apply(summarize, include_groups=False)
        .reset_index()
    )
    channel_summary = channel_summary[
        ["channel", "requests", "answered", "pending",
         "median_business_days", "on_time_rate"]
    ]

    df["year"] = df["in_date"].dt.year
    yearly = (
        df.groupby(["year", "channel"], sort=True)
        .agg(requests=("record_id", "size"), pending=("out_date", lambda values: values.isna().sum()),
             on_time_rate=("on_time", "mean"))
        .reset_index()
    )

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    entry = (
        df[df["out_date"].notna()]
        .groupby("day_name")
        .agg(
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
    )
    requests_by_day = df.groupby("day_name").size()
    entry_day = pd.DataFrame({"day_name": day_order})
    entry_day["requests"] = entry_day["day_name"].map(requests_by_day)
    entry_day["median_calendar_days"] = entry_day["day_name"].map(entry["median_calendar_days"])
    entry_day["median_business_days"] = entry_day["day_name"].map(entry["median_business_days"])

    submission = lab_dir / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    channel_summary.to_csv(submission / "channel_summary.csv", index=False)
    yearly.to_csv(submission / "yearly_summary.csv", index=False)
    entry_day.to_csv(submission / "entry_day_summary.csv", index=False)
    return channel_summary, yearly, entry_day
