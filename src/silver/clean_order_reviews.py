import os
from pathlib import Path
from dotenv import load_dotenv
from src.silver.utils import limpar_comentario
from src.config import spark
from pyspark.sql import functions as F

load_dotenv()
PASTA_BRONZE = Path(os.getenv("PASTA_BRONZE"))
PASTA_SILVER = Path(os.getenv("PASTA_SILVER"))


def processar_order_reviews():
    df_reviews = spark.read.parquet(f"{PASTA_BRONZE}/olist_order_reviews_dataset")

    df_reviews = df_reviews.dropDuplicates(["review_id", "order_id"])
    df_reviews = df_reviews.filter(F.col("review_score").between(1,5))

    df_reviews = (
        df_reviews
        .withColumn("review_creation_date",F.to_date(F.col("review_creation_date"), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("review_answer_timestamp", F.to_timestamp(F.col("review_answer_timestamp"),"yyyy-MM-dd HH:mm:ss"))
        .withColumn("review_score",F.col("review_score").cast("byte"))
        .withColumn("review_comment_title",limpar_comentario(F.col("review_comment_title")))
        .withColumn("review_comment_message",limpar_comentario(F.col("review_comment_message")))
        .withColumn("data_processamento_silver", F.current_timestamp())
    )

    PASTA_SILVER.mkdir(parents=True, exist_ok=True)
    caminho_saida = PASTA_SILVER / "reviews"
    df_reviews.write.mode("overwrite").parquet(str(caminho_saida))
    print("[SILVER] Tabela 'reviews' processada com sucesso.")


if __name__ == "__main__":
    processar_order_reviews()