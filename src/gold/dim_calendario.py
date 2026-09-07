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

def dim_calendario():
    df_orders = pd.read_parquet(PASTA_SILVER / "orders.parquet")

    data_min = df_orders["order_purchase_timestamp"].min()
    data_max = df_orders["order_purchase_timestamp"].max()

    datas = pd.date_range(start=data_min.date(), end=data_max.date(), freq="D")
    df_calendario = pd.DataFrame({"data": datas})

    df_calendario["ano"] = df_calendario["data"].dt.year
    df_calendario["mes"] = df_calendario["data"].dt.month
    df_calendario["ano_mes"] = df_calendario["data"].dt.strftime("%Y-%m")
    df_calendario["dia_semana"] = df_calendario["data"].dt.day_name()
    df_calendario["trimestre"] = df_calendario["data"].dt.quarter
    df_calendario["eh_fim_de_semana"] = df_calendario["data"].dt.dayofweek >= 5

    df_calendario.to_sql(name="dim_calendario",con=engine, if_exists="replace",chunksize=5000,method="multi",index=False)
    print("dim_calendario criada com sucesso.")

if __name__ == "__main__":
    dim_calendario()