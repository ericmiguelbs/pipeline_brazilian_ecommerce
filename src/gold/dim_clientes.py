import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.database import engine

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))
PASTA_GOLD_BI = Path(os.getenv("PASTA_GOLD_BI"))

PASTA_GOLD_BI.mkdir(parents=True, exist_ok=True)


def dim_clientes():
    df_customers = pd.read_parquet(PASTA_SILVER / "customers.parquet")
    df_geo = pd.read_parquet(PASTA_SILVER / "geolocation.parquet")

    dim_cliente = df_customers.merge(
        df_geo[
            [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
            ]
        ],
        left_on="customer_zip_code_prefix",
        right_on="geolocation_zip_code_prefix",
        how="left",
    ).drop(columns=["geolocation_zip_code_prefix"])

    dim_cliente.to_sql(name="dim_clientes",con=engine,if_exists="replace",method="multi",chunksize=5000,index=False)

    print("dim_clientes criada com sucesso.")

if __name__ == "__main__":
    dim_clientes()