import os
from pathlib import Path
from dotenv import load_dotenv
import kagglehub

from src.config import spark
from pyspark.sql import functions as F

load_dotenv()

PASTA_BRONZE = os.getenv("PASTA_BRONZE")
if not PASTA_BRONZE:
    raise ValueError("Variável PASTA_BRONZE não encontrada no ambiente.")

PASTA_BRONZE = Path(PASTA_BRONZE)


def obter_caminho_dados():
    return Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))


def executar_ingestao():
    caminho = obter_caminho_dados()
    PASTA_BRONZE.mkdir(parents=True, exist_ok=True)

    arquivos_csv = list(caminho.glob("*.csv"))
    print(f"[BRONZE] Encontrados {len(arquivos_csv)} arquivos para ingestão...")

    for arquivo_csv in arquivos_csv:
        nome_tabela = arquivo_csv.stem
        caminho_saida = PASTA_BRONZE / nome_tabela

        df = (
            spark.read
            .option("header", True)
            .csv(str(arquivo_csv))
            .withColumn("data_ingestao_bronze", F.current_timestamp())
            .withColumn("arquivo_origem", F.lit(arquivo_csv.name))
        )

        df.write.mode("overwrite").parquet(str(caminho_saida))
        print(f"[BRONZE] Tabela '{nome_tabela}' ingerida com sucesso.")

    print("[BRONZE] Ingestão concluída com sucesso.")


if __name__ == "__main__":
    executar_ingestao()