import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_payments():
    df_payments = pd.read_parquet(PASTA_BRONZE / "olist_order_payments_dataset.parquet")

    df_payments['payment_sequential'] = df_payments['payment_sequential'].astype('int8')
    df_payments['payment_installments'] = df_payments['payment_installments'].astype('int8')
    df_payments = df_payments.drop_duplicates(subset=['order_id','payment_sequential'])
    df_payments["data_processamento_silver"] = pd.Timestamp.now()
    df_payments = df_payments.loc[(df_payments['payment_value'] > 0)]

    df_payments.to_parquet(PASTA_SILVER / "order_payments.parquet", index=False)

if __name__ == "__main__":
    processar_order_payments()