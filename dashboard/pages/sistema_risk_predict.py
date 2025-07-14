import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join('.')))

# adicionando módulo próprio 
from src.model_utils import predict 

def show():

    st.markdown(
    """
        <style>
        .stProgress > div > div > div > div {
            background-color: #FFFFFF;  /* Cor branca para a barra de carregamento */
        }
        </style>
    """,
    unsafe_allow_html=True
    )


    st.title("Sistema Risk Predict")

    st.markdown("""
    Faça o upload de um arquivo `.csv`. O arquivo deve estar separado por ponto e vírgula (;). Certifique-se de que ele possua as colunas: ID_CLIENTE, SAFRA_REF, DATA_EMISSAO_DOCUMENTO, DATA_VENCIMENTO, VALOR A PAGAR e TAXA.
    """)

    uploaded_file = st.file_uploader("Upload do CSV", type="csv", help="O arquivo deve estar no formato .csv, separado por ponto e vírgula (;). Certifique-se de que ele possui as colunas: ID_CLIENTE, SAFRA_REF, DATA_EMISSAO_DOCUMENTO, DATA_VENCIMENTO, VALOR A PAGAR e TAXA.")
    

    if uploaded_file is not None:
        # Lê o CSV enviado
        df_teste = pd.read_csv(uploaded_file, sep=';')

        # Para mostrar o status do processamento
        placeholder_status = st.empty()

        # Barra de progresso
        progress_bar = st.progress(0)
        
        with st.spinner("Realizando a previsão..."):
            
            submissao_case = predict(df_teste, placeholder_status, progress_bar)
        

        # Mostra preview
        st.subheader("Prévia dos resultados (maiores chances de inadimplência)")
        top_10 = submissao_case.sort_values('PROBABILIDADE_INADIMPLENCIA', ascending=False).head(10)
        top_10['ID_CLIENTE'] = top_10['ID_CLIENTE'].astype(str) 
        st.dataframe(top_10, use_container_width=True)

        # Botão para baixar o resultado
        csv = submissao_case.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar resultado (.csv)",
            data=csv,
            file_name='submissao_case.csv',
            mime='text/csv'
        )

        # === Gráfico: Distribuição das probabilidades ===
        st.subheader("Distribuição das probabilidades de inadimplência")
        fig_hist = px.histogram(
            submissao_case,
            x='PROBABILIDADE_INADIMPLENCIA',
            nbins=50,
            title='Distribuição das probabilidades de inadimplência',
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(
            xaxis_title='Probabilidade',
            yaxis_title='Frequência',
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # === Gráfico: Pizza de risco >= 50% ===
        st.subheader("Proporção de clientes com risco elevado (≥ 50%)")
        alto_risco = submissao_case['PROBABILIDADE_INADIMPLENCIA'] >= 0.5
        n_alto_risco = alto_risco.sum()
        n_baixo_risco = len(submissao_case) - n_alto_risco

        fig_pizza = go.Figure(
            data=[go.Pie(
                labels=['Risco < 50%', 'Risco ≥ 50%'],
                values=[n_baixo_risco, n_alto_risco],
                marker=dict(colors=['#cce5ff', '#1f77b4']),
                textinfo='label+percent',
                insidetextorientation='radial'
            )]
        )
        fig_pizza.update_layout(
            title='Proporção de clientes com risco ≥ 50%',
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
