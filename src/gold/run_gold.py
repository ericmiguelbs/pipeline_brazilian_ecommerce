# run_gold.py
from src.gold.dim_clientes import dim_clientes
from src.gold.dim_produtos import dim_produtos
from src.gold.dim_calendario import dim_calendario
from src.gold.fato_vendas import fato_vendas

if __name__ == "__main__":
    print("Iniciando processamento da camada Gold...")
    dim_clientes()
    dim_produtos()
    dim_calendario()
    fato_vendas()
    
    print("Processamento finalizado!")