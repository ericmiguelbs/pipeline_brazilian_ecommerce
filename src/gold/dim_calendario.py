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


def dim_calendario():
    df_orders = spark.read.parquet(f"{PASTA_SILVER}/orders")

    limites = (
        df_orders.agg(
            F.min(F.to_date("order_purchase_timestamp")).alias("data_min"),
            F.max(F.to_date("order_purchase_timestamp")).alias("data_max")
        ).first()
    )

    data_inicio = limites["data_min"].strftime("%Y-%m-%d")
    data_fim = limites["data_max"].strftime("%Y-%m-%d")

    df_datas = (
        spark.sql(f"SELECT sequence(to_date('{data_inicio}'), to_date('{data_fim}'), interval 1 day) as datas")
        .select(F.explode("datas").alias("data"))
    )

    df_calendario = (
        df_datas
        .withColumn("sk_data", F.date_format(F.col("data"),"yyyyMMdd").cast("int"))
        .withColumn("ano", F.year(F.col("data")).cast("short"))
        .withColumn("mes", F.month(F.col("data")).cast("byte"))
        .withColumn("dia",F.dayofmonth(F.col("data")).cast("byte"))
        .withColumn("trimestre", F.quarter(F.col("data")).cast("byte"))
        .withColumn("dia_semana_num",F.dayofweek(F.col("data")).cast("byte"))
        .withColumn("dia_semana_nome",F.date_format(F.col("data"), "EEEE"))
        .withColumn("ano_mes", F.date_format(F.col("data"),"yyyy-MM"))
        .withColumn("flag_fim_semana", F.when(F.dayofweek(F.col("data")).isin(1,7),F.lit(1)).otherwise(F.lit(0)).cast("byte"))
        .withColumn("data_processamento_gold", F.current_timestamp())
    )


    URL_JDBC = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"

    (
        df_calendario.write
        .format("jdbc")
        .option("url", URL_JDBC)
        .option("dbtable", "dim_calendario")
        .option("user", PG_USER)
        .option("password", PG_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print("[GOLD] Tabela 'dim_calendario' inserida na base de dados com sucesso.")

if __name__ == "__main__":
    dim_calendario()