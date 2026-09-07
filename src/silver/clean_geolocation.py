import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from src.silver.utils import limpar_nome_cidade

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def moda(serie):
    return serie.mode().iloc[0] if not serie.mode().empty else None


def processar_geolocation():
    df_geolocation = pd.read_parquet(
        PASTA_BRONZE / "olist_geolocation_dataset.parquet"
    )

    df_geolocation["geolocation_zip_code_prefix"] = (
        df_geolocation["geolocation_zip_code_prefix"]
        .astype(float)
        .astype(int)
        .astype(str)
        .str.zfill(5)
    )

    df_geolocation["geolocation_city"] = (
        df_geolocation["geolocation_city"].str.strip().str.title()
    )
    df_geolocation["geolocation_state"] = (
        df_geolocation["geolocation_state"].str.strip().str.upper()
    )

    df_geolocation_grouped = (
        df_geolocation.groupby("geolocation_zip_code_prefix")
        .agg(
            {
                "geolocation_lat": "median",
                "geolocation_lng": "median",
                "geolocation_city": moda,
                "geolocation_state": moda,
            }
        )
        .reset_index()
    )
    df_geolocation_grouped["geolocation_city"] = df_geolocation_grouped[
        "geolocation_city"
    ].apply(limpar_nome_cidade)
    df_geolocation_grouped["data_processamento_silver"] = pd.Timestamp.now()

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    df_geolocation_grouped.to_parquet(
        PASTA_SILVER / "geolocation.parquet", index=False
    )
    print("geolocation.parquet processado com sucesso.")


if __name__ == "__main__":
    processar_geolocation()