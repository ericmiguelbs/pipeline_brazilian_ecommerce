import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from src.silver.utils import limpar_nomes

from src.config import spark
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_customers():
    df_customers = spark.read.parquet(f"{PASTA_BRONZE}/olist_customers_dataset")
    df_customers = df_customers.dropDuplicates(["customer_id"])

    df_customers = (
        df_customers
        .withColumn("customer_zip_code_prefix",F.lpad(F.col("customer_zip_code_prefix").cast(StringType()),5,"0"))
        .withColumn("customer_city",limpar_nomes(F.col("customer_city")))
        .withColumn("customer_state", F.upper(F.trim(F.col("customer_state"))))
        .withColumn("data_processamento_silver", F.current_timestamp())
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = PASTA_SILVER / "customers"
    df_customers.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'customers' processada com sucesso.")


if __name__ == "__main__":
    processar_customers()