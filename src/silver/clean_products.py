import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import spark
from pyspark.sql import functions as F

load_dotenv()

PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_products():
    df_products = spark.read.parquet(f"{PASTA_BRONZE}/olist_products_dataset")

    df_products = df_products.dropDuplicates(['product_id'])

    df_products = (
            df_products
            .withColumnRenamed("product_name_lenght","product_name_length")
            .withColumnRenamed("product_description_lenght","product_description_length")
        )

    df_products = df_products.fillna({
        "product_category_name":"não_informado",
        "product_name_length":0,
        "product_description_length":0,
        "product_photos_qty":0,
        "product_weight_g":0,
        "product_length_cm":0,
        "product_height_cm":0,
        "product_width_cm":0
        }
    )

    df_products = (
        df_products
        .withColumn("product_category_name", F.lower(F.trim(F.col("product_category_name"))))
        .withColumn("product_photos_qty", F.col("product_photos_qty").cast("byte"))
        .withColumn("data_processamento_silver", F.current_timestamp())
    )


    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = PASTA_SILVER / "products"
    df_products.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'products' processada com sucesso.")

if __name__ == "__main__":
    processar_products()
