import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_products():
    df_products = pd.read_parquet(PASTA_BRONZE / 'olist_products_dataset.parquet')

    df_products = df_products.drop_duplicates(subset=['product_id'], keep='first')

    df_products['product_category_name'] = df_products['product_category_name'].fillna('Não Informado')

    colunas_num = [
        'product_name_lenght', 'product_description_lenght','product_photos_qty','product_weight_g','product_length_cm',
        'product_height_cm', 'product_width_cm'
    ]

    df_products[colunas_num] = df_products[colunas_num].fillna(0)

    df_products = df_products.rename(columns={
        'product_name_lenght':'product_name_length',
        'product_description_lenght': 'product_description_length'
    })

    df_products['data_processamento_silver'] = pd.Timestamp.now()
    df_products.to_parquet(PASTA_SILVER / 'products.parquet', index=False)

if __name__ == "__main__":
    processar_products()
