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

def dim_produtos():
    df_produtos = pd.read_parquet(PASTA_SILVER / "products.parquet")
    df_produtos.to_sql(name="dim_produtos",con=engine,if_exists="replace",method="multi",index=False,chunksize=5000)

if __name__ == "__main__":
    dim_produtos()
