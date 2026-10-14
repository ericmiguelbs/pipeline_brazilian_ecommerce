# Opção 1: Importação absoluta (Recomendada)
from src.gold.dim_clientes import dim_clientes
from src.gold.dim_produtos import dim_produtos
from src.gold.dim_calendario import dim_calendario
from src.gold.dim_vendedores import dim_vendedores
from src.gold.fato_vendas import fato_vendas
from src.gold.fato_pagamentos import fato_pagamentos

def executar_gold():
    print("[GOLD] Iniciando tratamento da camada Gold...")
    dim_calendario()
    dim_produtos()
    dim_clientes()
    dim_vendedores()
    fato_vendas()
    fato_pagamentos()
    print("[GOLD] Camada Gold concluída com sucesso.")

if __name__ == "__main__":
    executar_gold()