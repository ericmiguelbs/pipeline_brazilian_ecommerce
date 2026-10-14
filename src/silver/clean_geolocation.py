import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import spark
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))

def processar_geolocation():
    df_geolocation = spark.read.parquet(f"{PASTA_BRONZE}/olist_geolocation_dataset")

    df_geolocation = (
        df_geolocation
        .withColumn("geolocation_zip_code_prefix",F.lpad(F.col("geolocation_zip_code_prefix").cast(StringType()),5,"0"))
        .withColumn("geolocation_city",F.trim(F.initcap(F.col("geolocation_city"))))
        .withColumn("geolocation_state", F.trim(F.upper(F.col("geolocation_state"))))
    )

    df_geolocation_grouped = (
        df_geolocation.groupBy("geolocation_zip_code_prefix").agg(
            F.percentile_approx("geolocation_lat",0.5).alias("geolocation_lat"),
            F.percentile_approx("geolocation_lng",0.5).alias("geolocation_lng"),
            F.mode("geolocation_city").alias("geolocation_city"),
            F.mode("geolocation_state").alias("geolocation_state")
        )
        .withColumn("data_processamento_silver", F.current_timestamp())
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = f"{PASTA_SILVER}/geolocation"
    df_geolocation_grouped.write.mode("overwrite").parquet(caminho_saida)
    print("[SILVER] Tabela 'geolocation' processada com sucesso.")


if __name__ == "__main__":
    processar_geolocation()