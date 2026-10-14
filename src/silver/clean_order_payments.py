import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import spark
from pyspark.sql import functions as F
from pyspark.sql.types import ByteType

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_payments():
    df_payments = spark.read.parquet(f"{PASTA_BRONZE}/olist_order_payments_dataset")

    df_payments = df_payments.dropDuplicates(["order_id","payment_sequential"])
    df_payments = df_payments.filter(F.col("payment_value") > 0)
    df_payments = (
        df_payments
        .withColumn("payment_sequential", F.col("payment_sequential").cast("byte"))
        .withColumn("payment_installments", F.col("payment_installments").cast("byte"))
        .withColumn("data_processamento_silver", F.current_timestamp())
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = f"{PASTA_SILVER}/payments"
    df_payments.write.mode("overwrite").parquet(caminho_saida)
    print("[SILVER] Tabela 'payments' processada com sucesso.")

if __name__ == "__main__":
    processar_order_payments()