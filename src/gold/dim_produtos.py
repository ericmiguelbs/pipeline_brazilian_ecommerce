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

def dim_produtos():
    df_produtos = spark.read.parquet(f"{PASTA_SILVER}/products")

    df_produtos = df_produtos.withColumn("data_processamento_gold", F.current_timestamp())
    URL_JDBC = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"
        
    (
        df_produtos.write
        .format("jdbc")
        .option("url", URL_JDBC)
        .option("dbtable", "dim_produtos")
        .option("user", PG_USER)
        .option("password", PG_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )
        
    print("[GOLD] Tabela 'dim_produtos' inserida na base de dados com sucesso.")



if __name__ == "__main__":
    dim_produtos()
