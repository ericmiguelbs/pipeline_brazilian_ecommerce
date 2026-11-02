import os
import io
import psycopg2
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
PORT = os.getenv("POSTGRES_PORT", "5432")
DB = os.getenv("POSTGRES_DB", "dw_gold")

# Detecção automática de ambiente:
# 1. Se estiver dentro de um contêiner Docker, o arquivo /.dockerenv existe.
#    Nesse caso, utiliza o host interno da rede Docker ("postgres_gold").
# 2. Se estiver rodando na máquina host (Windows), utiliza "localhost".
DOCKER_ENV = os.path.exists("/.dockerenv")

if DOCKER_ENV:
    HOST = os.getenv("POSTGRES_HOST", "postgres_gold")
else:
    HOST = "localhost"


def get_connection():
    """Retorna uma conexão ativa com o banco PostgreSQL dw_gold."""
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DB,
        user=USER,
        password=PASSWORD,
    )


def df_to_postgres(df, table_name, if_exists="replace"):
    """
    Grava um DataFrame no PostgreSQL utilizando psycopg2 e comando COPY.
    
    Parâmetros:
        df         : pandas DataFrame
        table_name : nome da tabela destino
        if_exists  : 'replace' (recria tabela) ou 'append' (insere novos dados)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if if_exists == "replace":
                cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')

                col_defs = []
                for col, dtype in df.dtypes.items():
                    if "int" in str(dtype):
                        pg_type = "BIGINT"
                    elif "float" in str(dtype):
                        pg_type = "DOUBLE PRECISION"
                    elif "bool" in str(dtype):
                        pg_type = "BOOLEAN"
                    elif "datetime" in str(dtype):
                        pg_type = "TIMESTAMP"
                    else:
                        pg_type = "TEXT"
                    col_defs.append(f'"{col}" {pg_type}')

                create_sql = f'CREATE TABLE "{table_name}" ({", ".join(col_defs)})'
                cur.execute(create_sql)

            buffer = io.StringIO()
            df.to_csv(buffer, index=False, header=False, na_rep="\\N")
            buffer.seek(0)

            columns = ", ".join(f'"{c}"' for c in df.columns)
            cur.copy_expert(
                f"COPY \"{table_name}\" ({columns}) FROM STDIN WITH CSV NULL '\\N'",
                buffer,
            )

        conn.commit()
    finally:
        conn.close()