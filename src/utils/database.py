import os
import io
import psycopg2
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

HOST = os.getenv("POSTGRES_HOST")
if not HOST or HOST in ("localhost", "127.0.0.1"):
    HOST = "postgres_gold"

PORT = os.getenv("POSTGRES_PORT", "5432")
DB = os.getenv("POSTGRES_DB", "dw_gold")


def get_connection():
    """Retorna uma conexão psycopg2 direta ao banco gold."""
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DB,
        user=USER,
        password=PASSWORD,
    )


def df_to_postgres(df, table_name, if_exists="replace"):
    """
    Grava um DataFrame no PostgreSQL usando psycopg2 + COPY.
    Evita dependência de SQLAlchemy nos scripts gold.

    Parâmetros:
        df         : pandas DataFrame
        table_name : nome da tabela destino
        if_exists  : 'replace' (drop + recreate) ou 'append'
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if if_exists == "replace":
                cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')

                # Cria tabela com base nos tipos do DataFrame
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

            # Serializa o DataFrame como CSV em memória e usa COPY
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
