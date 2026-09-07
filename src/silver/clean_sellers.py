import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from src.silver.utils import limpar_nome_cidade

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

def processar_sellers():
    df_sellers = pd.read_parquet(PASTA_BRONZE / 'olist_sellers_dataset.parquet')
    df_sellers = df_sellers.drop_duplicates(subset=['seller_id'])

    df_sellers['seller_zip_code_prefix'] = (df_sellers['seller_zip_code_prefix'].astype(float).astype(int).astype(str).str.zfill(5))

    df_sellers['seller_city'] = df_sellers['seller_city'].apply(limpar_nome_cidade)
    df_sellers['seller_state'] = df_sellers['seller_state'].str.upper()

    df_sellers['data_processamento_silver'] = pd.Timestamp.now()

    df_sellers.to_parquet(PASTA_SILVER / 'sellers.parquet', index=False)

if __name__ == "__main__":
    processar_sellers()