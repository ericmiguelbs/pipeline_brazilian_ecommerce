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

def fato_vendas():
    df_orders = spark.read.parquet(f"{PASTA_SILVER}/orders").select("order_id","customer_id","order_status","order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date")
    df_items = spark.read.parquet(f"{PASTA_SILVER}/order_items")

    fato_vendas = (
        df_items.join(
            F.broadcast(df_orders),
            on="order_id",
            how="inner"
        )
    )

    fato_vendas = (
        fato_vendas
        .withColumn("valor_total", (F.col("price") + F.col("freight_value")))
        .withColumn("data_compra", F.col("order_purchase_timestamp"))
        .withColumn("id_data_compra", F.date_format(F.col("data_compra"), "yyyyMMdd").cast("int"))
        .withColumn("tempo_entrega_dias", F.datediff("order_delivered_customer_date","order_purchase_timestamp"))
        .withColumn("dias_atraso", F.datediff("order_delivered_customer_date","order_estimated_delivery_date"))
        .withColumn("flag_atraso", F.when(F.col("dias_atraso")>0,1).otherwise(0))
        .withColumn("data_processamento_gold", F.current_timestamp())
        .drop("order_purchase_timestamp")
    )

    URL_JDBC = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"
    
    (
        fato_vendas.write
        .format("jdbc")
        .option("url", URL_JDBC)
        .option("dbtable", "fato_vendas")
        .option("user", PG_USER)
        .option("password", PG_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )
    
    print("[GOLD] Tabela 'fato_vendas' inserida na base de dados com sucesso.")



if __name__ == "__main__":
    fato_vendas()
