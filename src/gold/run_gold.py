from dim_clientes import dim_clientes
from dim_produtos import dim_produtos
from dim_calendario import dim_calendario
from fato_vendas import fato_vendas
from fato_payments import fato_payments

if __name__ == "__main__":
    print("Iniciando processamento da camada Gold...")
    dim_clientes()
    dim_produtos()
    dim_calendario()
    fato_vendas()
    fato_payments()
    
    print("Processamento finalizado!")