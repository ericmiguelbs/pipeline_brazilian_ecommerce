import os
from pathlib import Path
from dotenv import load_dotenv
from src.silver.utils import limpar_nome
from src.config import spark
from pyspark.sql import functions as F

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

def processar_sellers():
    df_sellers = spark.read.parquet(f"{PASTA_BRONZE}/olist_sellers_dataset")
    df_sellers = df_sellers.dropDuplicates(['seller_id'])

    df_sellers= (
        df_sellers
        .withColumn("seller_zip_code_prefix",F.lpad(F.col("seller_zip_code_prefix").cast("string"),5,"0"))
        .withColumn("seller_city",limpar_nome(F.col("seller_city")))
        .withColumn("seller_state",F.upper(F.col("seller_state")))
        .withColumn("data_processamento_silver", F.current_timestamp())  
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = PASTA_SILVER / "sellers"

    df_sellers.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'sellers' processada com sucesso.")

if __name__ == "__main__":
    processar_sellers()