import kagglehub
import pandas as pd
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
        df = pd.read_csv(arquivo_csv)

        df['data_ingestao_bronze'] = pd.Timestamp.now()
        df['arquivo_origem'] = arquivo_csv.name

        nome_tabela = arquivo_csv.stem
        caminho_saida = PASTA_BRONZE / f"{nome_tabela}.parquet"
        df.to_parquet(caminho_saida, index=False)
        print(f'Arquivo salvo: {caminho_saida}')