import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import spark
from pyspark.sql import functions as F
from pyspark.sql.types import ByteType

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_items():
    df_order_items = spark.read.parquet(f"{PASTA_BRONZE}/olist_order_items_dataset")

    df_order_items = df_order_items.dropDuplicates(["order_id","order_item_id"])
    df_order_items = df_order_items.filter((F.col("price")>=0) & (F.col("freight_value") >= 0))
    df_order_items = (
        df_order_items
        .withColumn("shipping_limit_date",F.to_timestamp(F.col("shipping_limit_date"), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("order_item_id", F.col("order_item_id").cast(ByteType()))
        .withColumn("data_processamento_silver", F.current_timestamp())
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = f"{PASTA_SILVER}/order_items"
    df_order_items.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'order_items' processada com sucesso.")

if __name__ == "__main__":
    processar_order_items()