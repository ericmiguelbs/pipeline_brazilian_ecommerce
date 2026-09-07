import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from src.silver.utils import limpar_nome_cidade

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_customers():
    df_customers = pd.read_parquet(PASTA_BRONZE / "olist_customers_dataset.parquet")
    df_customers = df_customers.drop_duplicates(subset=["customer_id"])

    df_customers["customer_zip_code_prefix"] = (
        df_customers["customer_zip_code_prefix"]
        .astype(float)
        .astype(int)
        .astype(str)
        .str.zfill(5)
    )

    df_customers["customer_city"] = df_customers["customer_city"].apply(
        limpar_nome_cidade
    )
    df_customers["customer_state"] = (
        df_customers["customer_state"].str.strip().str.upper()
    )
    df_customers["data_processamento_silver"] = pd.Timestamp.now()

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    df_customers.to_parquet(PASTA_SILVER / "customers.parquet", index=False)
    print("customers.parquet processado com sucesso.")


if __name__ == "__main__":
    processar_customers()