import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    from pathlib import Path

    import matplotlib.pyplot as plt

    lab_dir = Path(__file__).resolve().parents[1]
    df = pd.read_csv(lab_dir / "data" / "sales.csv.gz", compression="gzip")
    df["order_month"] = pd.to_datetime(df["OrderDate"], errors="coerce").dt.to_period("M")
    first = df.groupby("CustomerID")["order_month"].min()
    df["cohort_month"] = df["CustomerID"].map(first)
    df["period_index"] = (
        (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
        + df["order_month"].dt.month - df["cohort_month"].dt.month
    )

    cohort = (
        df.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    sizes = (
        cohort[cohort["period_index"] == 0]
        .set_index("cohort_month")["active_customers"]
    )
    cohort["cohort_size"] = cohort["cohort_month"].map(sizes)
    cohort["retention_rate"] = cohort["active_customers"] / cohort["cohort_size"]
    cohort["cohort_month"] = cohort["cohort_month"].astype(str)
    cohort = cohort[
        ["cohort_month", "period_index", "active_customers", "cohort_size", "retention_rate"]
    ].sort_values(["cohort_month", "period_index"])

    submission = lab_dir / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    cohort.to_csv(submission / "cohort_retention.csv", index=False)

    pivot = cohort.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pivot.values, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_xlabel("period_index")
    ax.set_ylabel("cohort_month")
    for row in range(pivot.shape[0]):
        for column in range(pivot.shape[1]):
            value = pivot.iloc[row, column]
            if pd.notna(value):
                ax.text(column, row, f"{value:.0%}", ha="center", va="center")
    fig.colorbar(im, ax=ax, label="retention_rate")
    fig.tight_layout()
    fig.savefig(submission / "cohort_retention_heatmap.png", dpi=150)
    plt.close(fig)
    return cohort
