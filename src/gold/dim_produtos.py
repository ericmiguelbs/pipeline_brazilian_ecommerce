import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))
PASTA_GOLD_BI = Path(os.getenv("PASTA_GOLD_BI"))

PASTA_GOLD_BI.mkdir(parents=True, exist_ok=True)

def dim_produtos():
    df_produtos = pd.read_parquet(PASTA_SILVER / "products.parquet")
    df_produtos.to_parquet(PASTA_GOLD_BI / "dim_products.parquet", index=False)