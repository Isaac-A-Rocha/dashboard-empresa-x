import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Empresa X", layout="wide")
sns.set(style="whitegrid")

# --- Conexão com o banco
conn = sqlite3.connect('empresa_x.db')
marcas = pd.read_sql("SELECT * FROM marcas", conn)
vendas = pd.read_sql("SELECT * FROM vendas_mensais", conn)
campanhas = pd.read_sql("SELECT * FROM campanhas", conn)
conn.close()

# --- Preparo dos dados
vendas['data'] = pd.to_datetime(dict(year=vendas['ano'], month=vendas['mes'], day=1))
vendas = vendas.merge(marcas, on='id_marca')

campanhas['mes'] = pd.to_datetime(campanhas['data_inicio']).dt.to_period('M').dt.to_timestamp()
campanhas = campanhas.merge(marcas, on='id_marca')

# --- Sidebar de filtro
st.sidebar.title("🔍 Filtros")
marca_selecionada = st.sidebar.selectbox("Escolha uma marca", marcas['nome_marca'])

# --- Filtragem por marca
vendas_marca = vendas[vendas['nome_marca'] == marca_selecionada]
campanhas_marca = campanhas[campanhas['nome_marca'] == marca_selecionada]

# --- KPIs principais
faturamento_total = vendas_marca['faturamento'].sum()
qtd_total = vendas_marca['qtd_vendas'].sum()

st.title(f"📊 Dashboard - {marca_selecionada}")
col1, col2 = st.columns(2)
col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
col2.metric("📦 Total de Vendas", f"{qtd_total:,}".replace(',', '.'))

# --- Gráfico de linha: Evolução do Faturamento
st.subheader("📈 Evolução Mensal do Faturamento")
if not vendas_marca.empty:
    fig, ax = plt.subplots()
    sns.lineplot(data=vendas_marca, x='data', y='faturamento', ax=ax, marker='o', color='blue')
    ax.set_ylabel("Faturamento (R$)")
    ax.set_xlabel("Data")
    ax.set_title("Faturamento Mensal")
    st.pyplot(fig)
else:
    st.info("🔎 Sem dados de faturamento para esta marca.")

# --- Gráfico de relação com campanhas
st.subheader("📊 Investimento vs Faturamento no mês da campanha")

# Agrupar vendas por mês
vendas_mensal = vendas_marca.groupby('data')[['faturamento']].sum().reset_index()
relacao = campanhas_marca.merge(vendas_mensal, left_on='mes', right_on='data', how='left')

if relacao.empty or relacao['faturamento'].isna().all():
    st.warning("⚠️ Esta marca ainda não tem campanhas com dados de faturamento no mês.")
else:
    relacao_plot = relacao[['nome_campanha', 'valor_investido', 'faturamento']].set_index('nome_campanha')
    relacao_plot = relacao_plot.fillna(0)

    fig2, ax2 = plt.subplots()
    relacao_plot.plot(kind='bar', ax=ax2, color=['#4CAF50', '#2196F3'])
    ax2.set_ylabel("R$ Valor")
    ax2.set_title("Investimento vs Faturamento por Campanha")
    ax2.legend(["Investimento", "Faturamento"])
    st.pyplot(fig2)

# --- Tabela de campanhas
st.subheader("📋 Campanhas da Marca")
if campanhas_marca.empty:
    st.info("🔎 Nenhuma campanha registrada para esta marca.")
else:
    st.dataframe(campanhas_marca[['nome_campanha', 'data_inicio', 'data_fim', 'valor_investido']])
