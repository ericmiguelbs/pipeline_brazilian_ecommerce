from src.silver.clean_customers import processar_customers
from src.silver.clean_geolocation import processar_geolocation
from src.silver.clean_order_items import processar_order_items
from src.silver.clean_order_payments import processar_order_payments
from src.silver.clean_order_reviews import processar_order_reviews
from src.silver.clean_orders import processar_orders
from src.silver.clean_products import processar_products
from src.silver.clean_sellers import processar_sellers


def main():
    etapas = [
        processar_customers,
        processar_geolocation,
        processar_order_items,
        processar_order_payments,
        processar_order_reviews,
        processar_orders,
        processar_products,
        processar_sellers,
    ]

    sucessos, falhas = [], []

    for etapa in etapas:
        try:
            etapa()
            sucessos.append(etapa.__name__)
        except Exception as e:
            falhas.append((etapa.__name__, str(e)))
            print(f"Erro em {etapa.__name__}: {e}")

    print(f"\n{len(sucessos)}/{len(etapas)} tabelas processadas com sucesso.")
    if falhas:
        print("Falhas detectadas:")
        for nome, erro in falhas:
            print(f" - {nome}: {erro}")


if __name__ == "__main__":
    main()