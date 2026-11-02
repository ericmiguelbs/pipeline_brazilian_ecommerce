import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.database import get_connection

st.set_page_config(
    page_title="E-Commerce Analytics - Olist",
    page_icon="📦",
    layout="wide"
)

@st.cache_data(ttl=3600)
def executar_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, con=conn)
    finally:
        conn.close()

st.title("Painel Executivo de Vendas & Logística - Olist")
st.markdown("Consumo analítico direto da camada **Gold** persistida no PostgreSQL.")

df_kpis = executar_query("""
    SELECT
        COUNT(DISTINCT order_id) AS total_pedidos,
        ROUND(SUM(valor_total)::numeric, 2) AS faturamento,
        ROUND(AVG(tempo_entrega_dias)::numeric, 1) AS media_entrega,
        ROUND(SUM(flag_atraso)::numeric / COUNT(order_id)::numeric * 100, 2) AS taxa_atraso
    FROM fato_vendas;
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Pedidos Únicos", f"{int(df_kpis['total_pedidos'][0]):,}".replace(",", "."))
col2.metric("Faturamento Total", f"R$ {df_kpis['faturamento'][0]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Tempo Médio de Entrega", f"{df_kpis['media_entrega'][0]} dias")
col4.metric("Taxa Geral de Atraso", f"{df_kpis['taxa_atraso'][0]}%")

st.divider()

tab_vendas, tab_logistica, tab_produtos_frete = st.tabs([
    "📈 Visão Geral & Vendas",
    "🚚 Logística & Prazos",
    "🏷️ Produtos & Impacto do Frete"
])

with tab_vendas:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("Faturamento Mensal (Histórico)")
        df_temporal = executar_query("""
            SELECT 
                c.ano_mes,
                ROUND(SUM(v.valor_total)::numeric, 2) AS faturamento,
                COUNT(DISTINCT v.order_id) AS total_pedidos
            FROM fato_vendas v
            INNER JOIN dim_calendario c ON v.id_data_compra = c.sk_data
            GROUP BY c.ano_mes
            ORDER BY c.ano_mes ASC;
        """)

        fig_faturamento = px.line(
            df_temporal,
            x="ano_mes",
            y="faturamento",
            markers=True,
            title="Evolução do Faturamento Mensal",
            labels={"ano_mes": "Mês/Ano", "faturamento": "Faturamento (R$)"}
        )
        fig_faturamento.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_faturamento, use_container_width=True)

    with col_graf2:
        st.subheader("Distribuição por Meio de Pagamento")
        df_pagamentos = executar_query("""
            SELECT 
                payment_type AS tipo_pagamento,
                ROUND(SUM(payment_value::numeric), 2) AS valor_total,
                COUNT(*) AS quantidade_transacoes
            FROM fato_pagamentos
            GROUP BY payment_type
            ORDER BY valor_total DESC;
        """)

        fig_pagamentos = px.pie(
            df_pagamentos,
            values="valor_total",
            names="tipo_pagamento",
            title="Volume Financeiro por Meio de Pagamento",
            hole=0.4
        )
        st.plotly_chart(fig_pagamentos, use_container_width=True)

    st.subheader("Comportamento de Parcelamento no Cartão")
    df_parcelas = executar_query("""
        SELECT 
            payment_installments AS parcelas,
            COUNT(*) AS total_transacoes,
            ROUND(SUM(payment_value::numeric), 2) AS volume_financeiro
        FROM fato_pagamentos
        WHERE payment_type = 'credit_card'
          AND payment_installments > 0
        GROUP BY payment_installments
        ORDER BY payment_installments ASC;
    """)

    fig_parcelas = px.bar(
        df_parcelas,
        x="parcelas",
        y="total_transacoes",
        title="Número de Transações por Quantidade de Parcelas (Cartão de Crédito)",
        labels={"parcelas": "Número de Parcelas", "total_transacoes": "Qtd. Transações"},
        text_auto=True
    )
    st.plotly_chart(fig_parcelas, use_container_width=True)

with tab_logistica:
    col_log1, col_log2 = st.columns(2)

    with col_log1:
        st.subheader("Top 10 Estados com Maior Tempo de Entrega")
        df_logistica_tempo = executar_query("""
            SELECT 
                cli.customer_state AS estado,
                COUNT(DISTINCT v.order_id) AS pedidos,
                ROUND(AVG(v.tempo_entrega_dias)::numeric, 1) AS media_dias_entrega,
                ROUND(SUM(v.flag_atraso)::numeric / COUNT(DISTINCT v.order_id)::numeric * 100, 2) AS taxa_atraso_pct
            FROM fato_vendas v
            INNER JOIN dim_cliente cli ON v.customer_id = cli.customer_id
            GROUP BY cli.customer_state
            HAVING COUNT(DISTINCT v.order_id) >= 100
            ORDER BY media_dias_entrega DESC
            LIMIT 10;
        """)

        fig_tempo = px.bar(
            df_logistica_tempo.sort_values("media_dias_entrega", ascending=True),
            x="media_dias_entrega",
            y="estado",
            orientation="h",
            color="taxa_atraso_pct",
            color_continuous_scale="Reds",
            title="Tempo Médio (Dias) colorido pela Taxa de Atraso (%)",
            labels={
                "estado": "Estado (UF)",
                "media_dias_entrega": "Média de Dias",
                "taxa_atraso_pct": "% Atraso"
            },
            text_auto=True
        )
        st.plotly_chart(fig_tempo, use_container_width=True)

    with col_log2:
        st.subheader("Diagnóstico Logístico por Estado (Quadrantes)")
        df_logistica_scatter = executar_query("""
            SELECT 
                cli.customer_state AS estado,
                COUNT(DISTINCT v.order_id) AS pedidos,
                ROUND(AVG(v.tempo_entrega_dias)::numeric, 1) AS media_dias_entrega,
                ROUND(SUM(v.flag_atraso)::numeric / COUNT(DISTINCT v.order_id)::numeric * 100, 2) AS taxa_atraso_pct
            FROM fato_vendas v
            INNER JOIN dim_cliente cli ON v.customer_id = cli.customer_id
            GROUP BY cli.customer_state
            HAVING COUNT(DISTINCT v.order_id) >= 50;
        """)

        fig_scatter = px.scatter(
            df_logistica_scatter,
            x="media_dias_entrega",
            y="taxa_atraso_pct",
            size="pedidos",
            color="taxa_atraso_pct",
            text="estado",
            color_continuous_scale="Blues",
            title="Tempo Médio vs. Taxa de Atraso (Tamanho = Volume de Pedidos)",
            labels={
                "media_dias_entrega": "Tempo Médio (Dias)",
                "taxa_atraso_pct": "Taxa de Atraso (%)",
                "pedidos": "Total Pedidos"
            }
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)


with tab_produtos_frete:
    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        st.subheader("Top 10 Categorias por Faturamento")
        df_categorias = executar_query("""
            SELECT 
                p.product_category_name AS categoria,
                ROUND(SUM(v.valor_total)::numeric, 2) AS faturamento,
                COUNT(DISTINCT v.order_id) AS total_pedidos
            FROM fato_vendas v
            INNER JOIN dim_produtos p ON v.product_id = p.product_id
            WHERE p.product_category_name IS NOT NULL
            GROUP BY p.product_category_name
            ORDER BY faturamento DESC
            LIMIT 10;
        """)

        fig_cat = px.bar(
            df_categorias.sort_values("faturamento", ascending=True),
            x="faturamento",
            y="categoria",
            orientation="h",
            title="Faturamento Total Acumulado (R$)",
            labels={"categoria": "Categoria", "faturamento": "Faturamento (R$)"},
            text_auto=True
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_prod2:
        st.subheader("Frete Médio por Categoria (Top 10 em Vendas)")
        df_frete = executar_query("""
            SELECT 
                p.product_category_name AS categoria,
                ROUND(AVG(v.freight_value::numeric), 2) AS media_frete,
                ROUND((SUM(v.freight_value::numeric) / NULLIF(SUM(v.valor_total::numeric), 0) * 100), 1) AS pct_frete_total
            FROM fato_vendas v
            INNER JOIN dim_produtos p ON v.product_id = p.product_id
            WHERE p.product_category_name IS NOT NULL
            GROUP BY p.product_category_name
            ORDER BY SUM(v.valor_total::numeric) DESC
            LIMIT 10;
        """)

        fig_frete = px.bar(
            df_frete.sort_values("media_frete", ascending=True),
            x="media_frete",
            y="categoria",
            orientation="h",
            color="pct_frete_total",
            color_continuous_scale="Viridis",
            title="Custo Médio de Frete (R$) e % sobre o Total",
            labels={
                "categoria": "Categoria",
                "media_frete": "Frete Médio (R$)",
                "pct_frete_total": "Frete / Total (%)"
            },
            text_auto=True
        )
        st.plotly_chart(fig_frete, use_container_width=True)