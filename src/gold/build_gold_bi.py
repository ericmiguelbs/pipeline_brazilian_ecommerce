import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))
PASTA_GOLD_BI = Path(os.getenv("PASTA_GOLD_BI"))

PASTA_GOLD_BI.mkdir(parents=True, exist_ok=True)


def dim_clientes():
    df_customers = pd.read_parquet(PASTA_SILVER / "customers.parquet")
    df_geo = pd.read_parquet(PASTA_SILVER / "geolocation.parquet")

    dim_cliente = df_customers.merge(
        df_geo[
            [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
            ]
        ],
        left_on="customer_zip_code_prefix",
        right_on="geolocation_zip_code_prefix",
        how="left",
    ).drop(columns=["geolocation_zip_code_prefix"])

    dim_cliente.to_parquet(PASTA_GOLD_BI / "dim_customers.parquet", index=False)
    print("dim_customers criada com sucesso.")


def dim_produtos():
    df_produto = pd.read_parquet(PASTA_SILVER / "products.parquet")
    df_produto.to_parquet(PASTA_GOLD_BI / "dim_products.parquet", index=False)
    print("dim_products criada com sucesso.")


def criar_dim_calendario():
    df_orders = pd.read_parquet(PASTA_SILVER / "orders.parquet")

    data_min = df_orders["order_purchase_timestamp"].min()
    data_max = df_orders["order_purchase_timestamp"].max()

    datas = pd.date_range(start=data_min.date(), end=data_max.date(), freq="D")
    df_calendario = pd.DataFrame({"data": datas})

    df_calendario["ano"] = df_calendario["data"].dt.year
    df_calendario["mes"] = df_calendario["data"].dt.month
    df_calendario["ano_mes"] = df_calendario["data"].dt.strftime("%Y-%m")
    df_calendario["dia_semana"] = df_calendario["data"].dt.day_name()
    df_calendario["trimestre"] = df_calendario["data"].dt.quarter
    df_calendario["eh_fim_de_semana"] = df_calendario["data"].dt.dayofweek >= 5

    df_calendario.to_parquet(
        PASTA_GOLD_BI / "dim_calendario.parquet", index=False
    )
    print("dim_calendario criada com sucesso.")


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


if __name__ == "__main__":
    dim_clientes()
    dim_produtos()
    criar_dim_calendario()
    fato_vendas()