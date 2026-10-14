import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.config import spark
from pyspark.sql import functions as F

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")


def fato_pagamentos():
    colunas_pagamentos = [
        "order_id",
        "payment_type",
        "payment_installments",
        "payment_value"
    ]

    df_payments = spark.read.parquet(f"{PASTA_SILVER}/payments").select(*colunas_pagamentos)
    df_orders = spark.read.parquet(f"{PASTA_SILVER}/orders").select("order_id","customer_id", "order_purchase_timestamp")

    fato_pagamentos = (
        df_payments.join(
            F.broadcast(df_orders),
            on="order_id",
            how="inner"
        )
    )

    fato_pagamentos =(
        fato_pagamentos
        .withColumn("data_compra", F.to_timestamp("order_purchase_timestamp", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("flag_parcelamento", F.when(F.col("payment_installments") > 1, 1).otherwise(0))
        .withColumn("id_data_compra", F.date_format(F.col("data_compra"), "yyyyMMdd").cast("int"))
        .withColumn("vlr_medio_parcela", F.when(F.col("payment_installments")>0, (F.col("payment_value")/F.col("payment_installments"))).otherwise(F.col("payment_value")))
        .withColumn("data_processamento_gold", F.current_timestamp())
        .drop("order_purchase_timestamp")
        )
    
    URL_JDBC = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"
    (
        fato_pagamentos.write
        .format("jdbc")
        .option("url", URL_JDBC)
        .option("dbtable", "fato_pagamentos")
        .option("user", PG_USER)
        .option("password", PG_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print("[GOLD] Tabela 'fato_pagamentos' inserida na base de dados com sucesso.")

if __name__ == "__main__":
    fato_pagamentos()
