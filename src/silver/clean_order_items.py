import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_items():
    df_order_items = pd.read_parquet(PASTA_BRONZE / "olist_order_items_dataset.parquet")

    df_order_items = df_order_items.drop_duplicates(subset=['order_id','order_item_id'])
    df_order_items['shipping_limit_date'] = pd.to_datetime(df_order_items['shipping_limit_date'])
    df_order_items['order_item_id'] = df_order_items['order_item_id'].astype('int8')
    df_order_items = df_order_items[(df_order_items['price'] >= 0) & (df_order_items['freight_value'] >=0)]
    df_order_items["data_processamento_silver"] = pd.Timestamp.now()

    df_order_items.to_parquet(PASTA_SILVER / "order_items.parquet", index=False)

if __name__ == "__main__":
    processar_order_items()