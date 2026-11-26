import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    from pathlib import Path

    lab_dir = Path(__file__).resolve().parents[1]
    df = pd.read_csv(
        lab_dir / "data" / "superstore_orders.csv.gz",
        compression="gzip",
        sep=";",
        decimal=",",
        encoding="latin1",
    )
    df["lost_profit"] = df["Profit"].clip(upper=0).abs()
    df["loss"] = df["Profit"] < 0

    lines = len(df)
    sales = df["Sales"].sum()
    profit = df["Profit"].sum()
    summary = pd.DataFrame([{
        "lines": lines,
        "orders": df["Order ID"].nunique(),
        "sales": sales,
        "profit": profit,
        "profit_margin": profit / sales,
        "loss_lines": int(df["loss"].sum()),
        "loss_line_rate": df["loss"].mean(),
        "lost_profit": df["lost_profit"].sum(),
    }])

    def discount_band(discount):
        if discount == 0:
            return "0%"
        if discount <= 0.05:
            return "1%-5%"
        if discount <= 0.10:
            return "6%-10%"
        return "más de 10%"

    df["discount_band"] = df["Discount"].map(discount_band)
    order = ["0%", "1%-5%", "6%-10%", "más de 10%"]
    discount = (
        df.groupby("discount_band")
        .agg(lines=("Sales", "size"), sales=("Sales", "sum"), profit=("Profit", "sum"),
             loss_line_rate=("loss", "mean"), lost_profit=("lost_profit", "sum"))
        .reindex(order)
        .reset_index()
    )
    discount["profit_margin"] = discount["profit"] / discount["sales"]
    discount = discount[
        ["discount_band", "lines", "sales", "profit", "profit_margin",
         "loss_line_rate", "lost_profit"]
    ]

    segment = (
        df.groupby(["Customer Segment", "Product Category"])
        .agg(lines=("Sales", "size"), sales=("Sales", "sum"), profit=("Profit", "sum"),
             lost_profit=("lost_profit", "sum"))
        .reset_index()
    )
    segment = segment[segment["lines"] >= 100]
    segment["profit_margin"] = segment["profit"] / segment["sales"]
    segment = segment.sort_values("lost_profit", ascending=False).head(5)
    segment = segment[
        ["Customer Segment", "Product Category", "lines", "sales", "profit",
         "profit_margin", "lost_profit"]
    ]

    submission = lab_dir / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    summary.to_csv(submission / "profitability_summary.csv", index=False)
    discount.to_csv(submission / "discount_summary.csv", index=False)
    segment.to_csv(submission / "priority_segments.csv", index=False)
    return summary, discount, segment
