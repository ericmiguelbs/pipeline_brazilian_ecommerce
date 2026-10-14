import kagglehub
from src.config import spark
from pyspark.sql import functions as F
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PASTA_BRONZE = os.getenv("PASTA_BRONZE")

if not PASTA_BRONZE:
    raise ValueError(
        "Variável PASTA_BRONZE não encontrada. "
    )

PASTA_BRONZE = Path(PASTA_BRONZE)


def caminho_dados():
    return kagglehub.dataset_download("olistbr/brazilian-ecommerce")


if __name__ == "__main__":
    caminho = Path(caminho_dados())

    PASTA_BRONZE.mkdir(parents=True, exist_ok=True)

    for arquivo_csv in caminho.glob("*.csv"):
        df = (
            spark.read.format("csv")
            .option("header",True)
            .option("inferSchema",True)
            .load(str(arquivo_csv))
        )

        df = df.withColumn("data_ingestao_bronze", F.current_timestamp())
        df = df.withColumn("arquivo_origem", F.lit(arquivo_csv.name))

        nome_tabela = arquivo_csv.stem
        caminho_saida = PASTA_BRONZE / nome_tabela

        df.write.mode("overwrite").parquet(str(caminho_saida))
        print(f"Tabela salva em: {caminho_saida}")