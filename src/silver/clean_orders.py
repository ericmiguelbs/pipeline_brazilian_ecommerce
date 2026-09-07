import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

def processar_orders():
    df_orders = pd.read_parquet(PASTA_BRONZE / 'olist_orders_dataset.parquet')

    df_orders = df_orders.drop_duplicates(subset=['order_id','customer_id'])

    df_orders['order_status'] = df_orders['order_status'].str.strip().str.lower()
    datas = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]

    for data in datas:
        df_orders[data] = pd.to_datetime(df_orders[data])

    df_orders['data_processamento_silver'] = pd.Timestamp.now()

    df_orders.to_parquet(PASTA_SILVER / "orders.parquet", index=False)

if __name__ == "__main__":
    processar_orders()