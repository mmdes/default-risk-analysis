import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

def show():
    # Carregando os dados processados
    @st.cache_data
    def carregar_dados():
        return pd.read_csv("./data/processed/merged_dataset.csv")

    df = carregar_dados()

    #st.set_page_config(page_title="Análise Exploratória de Dados", layout="wide")
    st.title("Análise Exploratória de Dados - Inadimplência")

    # ===== VISÃO GERAL =====
    st.header("1. Visão Geral da Base de Dados")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Registros", df.shape[0])
        st.metric("Colunas", df.shape[1])
    with col2:
        st.write("Tipos de Dados:")
        st.dataframe(df.dtypes.reset_index().rename(columns={0: "Tipo", "index": "Coluna"}))

    # ===== VALORES NULOS =====
    st.header("2. Valores Nulos por Coluna")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        st.bar_chart(missing)
    else:
        st.success("Nenhum valor nulo na base de dados!")

    # ===== DISTRIBUIÇÃO CLASSE =====
    st.header("3. Distribuição da Variável Alvo (Inadimplência)")
    fig_pie = px.pie(df, names='TARGET_INADIMPLENCIA', title='Distribuição de Adimplentes x Inadimplentes',
                     color='TARGET_INADIMPLENCIA',
                     color_discrete_map={0: 'lightgreen', 1: 'salmon'})
    st.plotly_chart(fig_pie)

    # ===== DISTRIBUIÇÃO DE VARIÁVEIS =====
    st.header("4. Distribuição de Variáveis")
    coluna = st.selectbox("Escolha a variável para visualizar a distribuição:", df.select_dtypes(include=['int', 'float']).columns)
    fig = px.histogram(df, x=coluna, nbins=30, color_discrete_sequence=["steelblue"])
    st.plotly_chart(fig)

    # ===== RELAÇÃO TAXA X INADIMPLÊNCIA =====
    st.header("5. Relação entre TAXA e Inadimplência")
    taxa_df = df.groupby("TAXA")["TARGET_INADIMPLENCIA"].agg(["mean", "count"]).reset_index()
    taxa_df.columns = ["TAXA", "Taxa de Inadimplência", "Quantidade"]
    fig_taxa = px.line(taxa_df, x="TAXA", y="Taxa de Inadimplência", markers=True)
    st.plotly_chart(fig_taxa)

    # ===== RELAÇÃO DOMINIO EMAIL X INADIMPLÊNCIA =====
    st.header("6. Taxa de Inadimplência por Domínio de E-mail")
    dom_email = df.groupby('DOMINIO_EMAIL')['TARGET_INADIMPLENCIA'].mean().reset_index()
    dom_email.columns = ['DOMINIO_EMAIL', 'Taxa de Inadimplência']
    fig_dom = px.bar(dom_email, x='Taxa de Inadimplência', y='DOMINIO_EMAIL', orientation='h')
    st.plotly_chart(fig_dom)

    # ===== DISTRIBUIÇÃO CEP_2_DIG =====
    st.header("7. Distribuição de Registros por Região (CEP_2_DIG)")
    fig_cep = px.histogram(df, x='CEP_2_DIG', color_discrete_sequence=['#2ca02c'])
    st.plotly_chart(fig_cep)

    # ===== OUTLIERS EM VALOR_A_PAGAR =====
    st.header("8. Boxplot de VALOR_A_PAGAR por PORTE")
    df_clean = df.dropna(subset=['VALOR_A_PAGAR', 'PORTE'])
    fig_box = px.box(df_clean, x='PORTE', y='VALOR_A_PAGAR', log_y=True, points='outliers')
    st.plotly_chart(fig_box)

    # ===== CORRELAÇÃO =====
    st.header("9. Correlação com a variável TARGET")
    numeric_cols = df.select_dtypes(include=['int64', 'float64'])
    corrs = numeric_cols.corr()['TARGET_INADIMPLENCIA'].drop('TARGET_INADIMPLENCIA').sort_values(ascending=False)
    st.bar_chart(corrs)

    # ===== TABELA FINAL =====
    st.header("10. Exibição Final do Dataset")
    if st.checkbox("Mostrar dados completos"):
        st.dataframe(df)

    st.markdown("---")
    st.caption("EDA para Case de Inadimplência")
