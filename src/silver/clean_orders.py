import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import spark
from pyspark.sql import functions as F

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

def processar_orders():
    df_orders = spark.read.parquet(f"{PASTA_BRONZE}/olist_orders_dataset")

    df_orders = df_orders.dropDuplicates(['order_id'])

    colunas = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]

    for coluna in colunas:
        df_orders = df_orders.withColumn(coluna, F.to_timestamp(F.col(coluna),"yyyy-MM-dd HH:mm:ss"))
    df_orders = (
        df_orders
        .withColumn("order_status", F.lower(F.trim(F.col("order_status"))))
        .withColumn("data_processamento_silver", F.current_timestamp())    
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = PASTA_SILVER / "orders"
    df_orders.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'orders' processada com sucesso.")

if __name__ == "__main__":
    processar_orders()