import pandas as pd
import os

df = pd.read_parquet(r"C:\Users\ericm\OneDrive\Área de Trabalho\dados_vendas\data\gold\bi\fato_payments.parquet")

print(df)