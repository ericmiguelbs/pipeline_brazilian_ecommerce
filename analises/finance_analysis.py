import os
import sys
import pandas as pd

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
# from data.bronze.dowload_dados import caminho_dados

# path = caminho_dados()

# caminho_customers = os.path.join(path,"olist_customers_dataset.csv")
# df_customers = pd.read_csv(caminho_customers)

# df_customers['customer_zip_code_prefix'] = (
#     df_customers['customer_zip_code_prefix']
#     .astype(str)
#     .str.zfill(5)
# )

# df_customers['customer_city'] = df_customers['customer_city'].str.title()
# df_customers['customer_state'] = df_customers['customer_state'].str.upper()

# print(df_customers.head())

pasta = r'C:\Users\ericm\.cache\kagglehub\datasets\olistbr\brazilian-ecommerce\versions\2'
arquivos = os.listdir(pasta)

for arquivo in arquivos:
    print(arquivo)