import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from src.silver.utils import limpar_comentario

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_reviews():
    df_reviews = pd.read_parquet(PASTA_BRONZE / "olist_order_reviews_dataset.parquet")
    df_reviews = df_reviews.drop_duplicates(subset=["review_id", "order_id"])

    df_reviews["review_creation_date"] = pd.to_datetime(
        df_reviews["review_creation_date"]
    )
    df_reviews["review_answer_timestamp"] = pd.to_datetime(
        df_reviews["review_answer_timestamp"]
    )
    df_reviews = df_reviews[df_reviews["review_score"].between(1, 5)]
    df_reviews["review_score"] = df_reviews["review_score"].astype("int8")

    df_reviews["review_comment_title"] = df_reviews["review_comment_title"].apply(
        limpar_comentario
    )
    df_reviews["review_comment_message"] = df_reviews["review_comment_message"].apply(
        limpar_comentario
    )

    df_reviews["data_processamento_silver"] = pd.Timestamp.now()

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    df_reviews.to_parquet(PASTA_SILVER / "order_reviews.parquet", index=False)
    print("order_reviews.parquet processado com sucesso.")


if __name__ == "__main__":
    processar_order_reviews()