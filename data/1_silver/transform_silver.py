from pathlib import Path
import pandas as pd
import unicodedata
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def limpar_nome_cidade(texto):
        if pd.isna(texto):
            return texto

        texto_normalizado = unicodedata.normalize("NFD", str(texto))

        texto_sem_acento = "".join(
            c for c in texto_normalizado if unicodedata.category(c) != "Mn"
        )

        texto_limpo = " ".join(texto_sem_acento.split())

        texto_final = texto_limpo.title()

        conectores = [" De ", " Do ", " Da ", " Dos ", " Das "]
        for conector in conectores:
            texto_final = texto_final.replace(conector, conector.lower())

        return texto_final

def limpar_comentario(texto):
    if pd.isna(texto):
        return texto
    texto_limpo = " ".join(str(texto).split())

    return texto_limpo if texto_limpo else np.nan


def processar_customers():
    df_customers = pd.read_parquet(PASTA_BRONZE / "olist_customers_dataset.parquet")

    df_customers = df_customers.drop_duplicates(subset=["customer_id"])

    df_customers['customer_zip_code_prefix'] = (
        df_customers['customer_zip_code_prefix']
        .astype(float).astype(int).astype(str)
        .str.zfill(5)
    )

    df_customers['customer_city'] = df_customers['customer_city'].apply(limpar_nome_cidade)
    df_customers['customer_state'] = df_customers['customer_state'].str.strip().str.upper()

    df_customers["data_processamento_silver"] = pd.Timestamp.now()

    df_customers.to_parquet(PASTA_SILVER / "customers.parquet", index=False)

def processar_geolocation():
    df_geolocation = pd.read_parquet(PASTA_BRONZE / "olist_geolocation_dataset.parquet")

    df_geolocation['geolocation_zip_code_prefix'] = (
        df_geolocation['geolocation_zip_code_prefix']
        .astype(float).astype(int).astype(str)
        .str.zfill(5)
    )

    df_geolocation["geolocation_city"] = (
            df_geolocation["geolocation_city"].str.strip().str.title()
        )
    df_geolocation["geolocation_state"] = (
            df_geolocation["geolocation_state"].str.strip().str.upper()
        )

    def moda(serie):
        return serie.mode().iloc[0] if not serie.mode().empty else None
    
    df_geolocation_grouped = (
        df_geolocation.groupby("geolocation_zip_code_prefix")
        .agg({
            "geolocation_lat": "median",
            "geolocation_lng": "median",
            "geolocation_city": moda,
            "geolocation_state": moda,
        })
        .reset_index()
    )
    df_geolocation_grouped['geolocation_city'] = df_geolocation_grouped['geolocation_city'].apply(limpar_nome_cidade)
    df_geolocation_grouped["data_processamento_silver"] = pd.Timestamp.now()
    

    df_geolocation_grouped.to_parquet(PASTA_SILVER / 'geolocation.parquet', index=False)

def processar_order_items():
    df_order_items = pd.read_parquet(PASTA_BRONZE / "olist_order_items_dataset.parquet")

    df_order_items = df_order_items.drop_duplicates(subset=['order_id','order_item_id'])
    df_order_items['shipping_limit_date'] = pd.to_datetime(df_order_items['shipping_limit_date'])
    df_order_items['order_item_id'] = df_order_items['order_item_id'].astype('int8')
    df_order_items = df_order_items[(df_order_items['price'] >= 0) & (df_order_items['freight_value'] >=0)]
    df_order_items["data_processamento_silver"] = pd.Timestamp.now()

    df_order_items.to_parquet(PASTA_SILVER / "order_items.parquet", index=False)


def processar_order_payments():
    df_payments = pd.read_parquet(PASTA_BRONZE / "olist_order_payments_dataset.parquet")

    df_payments['payment_sequential'] = df_payments['payment_sequential'].astype('int8')
    df_payments['payment_installments'] = df_payments['payment_installments'].astype('int8')
    df_payments = df_payments.drop_duplicates(subset=['order_id','payment_sequential'])
    df_payments["data_processamento_silver"] = pd.Timestamp.now()
    df_payments = df_payments.loc[(df_payments['payment_value'] > 0)]

    df_payments.to_parquet(PASTA_SILVER / "order_payments.parquet", index=False)

def processar_order_reviews():
    df_reviews = pd.read_parquet(PASTA_BRONZE / 'olist_order_reviews_dataset.parquet')
    df_reviews = df_reviews.drop_duplicates(subset=['review_id','order_id'])

    df_reviews['review_creation_date'] = pd.to_datetime(df_reviews['review_creation_date'])
    df_reviews['review_answer_timestamp'] = pd.to_datetime(df_reviews['review_answer_timestamp'])
    df_reviews = df_reviews[df_reviews['review_score'].between(1,5)]
    df_reviews['review_score'] = df_reviews['review_score'].astype('int8')

    df_reviews['review_comment_title'] = df_reviews['review_comment_title'].apply(limpar_comentario)
    df_reviews['review_comment_message'] = df_reviews['review_comment_message'].apply(limpar_comentario)


    df_reviews["data_processamento_silver"] = pd.Timestamp.now()

    df_reviews.to_parquet(PASTA_SILVER / "order_reviews.parquet", index=False)


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

    

def processar_sellers():
    df_sellers = pd.read_parquet(PASTA_BRONZE / 'olist_sellers_dataset.parquet')
    df_sellers = df_sellers.drop_duplicates(subset=['seller_id'])

    df_sellers['seller_zip_code_prefix'] = (df_sellers['seller_zip_code_prefix'].astype(float).astype(int).astype(str).str.zfill(5))

    df_sellers['seller_city'] = df_sellers['seller_city'].apply(limpar_nome_cidade)
    df_sellers['seller_state'] = df_sellers['seller_state'].str.upper()

    df_sellers['data_processamento_silver'] = pd.Timestamp.now()

    df_sellers.to_parquet(PASTA_SILVER / 'sellers.parquet', index=False)

def main():
    funcoes = [
        processar_customers,
        processar_geolocation,
        processar_order_items,
        processar_order_payments,
        processar_order_reviews,
        processar_orders,
        processar_products,
        processar_sellers,
    ]

    sucesso = []
    falhas = []

    for func in funcoes:
        try:
            func()
            sucesso.append(func.__name__)
            print(f"{func.__name__} concluída")
        except Exception as e:
            falhas.append((func.__name__, str(e)))
            print(f"{func.__name__} falhou: {e}")

    print(f"\n{len(sucesso)}/{len(funcoes)} tabelas processadas com sucesso")
    if falhas:
        print("Falhas:")
        for nome, erro in falhas:
            print(f"  - {nome}: {erro}")

if __name__ == "__main__":
    main()