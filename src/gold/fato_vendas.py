import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))
PASTA_GOLD_BI = Path(os.getenv("PASTA_GOLD_BI"))

PASTA_GOLD_BI.mkdir(parents=True, exist_ok=True)

def fato_vendas():
    df_orders = pd.read_parquet(PASTA_SILVER / "orders.parquet")
    df_items = pd.read_parquet(PASTA_SILVER / "order_items.parquet")

    fato = df_items.merge(
        df_orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        ],
        on="order_id",
        how="inner",
    )

    fato["valor_total"] = fato["price"] + fato["freight_value"]

    fato["data_compra"] = pd.to_datetime(
        fato["order_purchase_timestamp"].dt.date
    )

    fato["tempo_entrega_dias"] = (
        fato["order_delivered_customer_date"]
        - fato["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    fato["dias_atraso"] = (
        fato["order_delivered_customer_date"]
        - fato["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    fato["foi_atrasado"] = (fato["dias_atraso"] > 0).astype(int)

    fato.to_parquet(PASTA_GOLD_BI / "fato_vendas.parquet", index=False)
    print("fato_vendas criada com sucesso.")
