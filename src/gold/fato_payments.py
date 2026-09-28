import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.database import df_to_postgres

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def fato_payments():
    colunas_pagamentos = [
        "order_id",
        "payment_type",
        "payment_installments",
        "payment_value"
    ]

    df_payments = pd.read_parquet(PASTA_SILVER / "order_payments.parquet", columns=colunas_pagamentos)
    df_orders = pd.read_parquet(PASTA_SILVER / "orders.parquet")

    fato = df_payments.merge(
        df_orders[
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
            ]
        ],
        on="order_id",
        how="inner"
    )

    fato["data_compra"] = pd.to_datetime(
        fato["order_purchase_timestamp"].dt.date
    )

    fato["flag_parcelado"] = (fato["payment_installments"] > 1).astype(int)

    fato["vlr_medio_parcela"] = np.where(
        fato["payment_installments"] > 0,
        fato["payment_value"] / fato["payment_installments"],
        fato["payment_value"]
    )

    fato = fato.drop(columns=["order_purchase_timestamp"])

    df_to_postgres(fato, "fato_payments")
    print("Tabela fato_payments criada com sucesso.")


if __name__ == "__main__":
    fato_payments()
