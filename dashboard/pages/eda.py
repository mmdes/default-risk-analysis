import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def show():

    # Carregamento de dados
    @st.cache_data
    def carregar_dados():
        return pd.read_csv("./data/processed/dataset_features_v1.csv")

    # Dados
    df = carregar_dados()
    df["DATA_EMISSAO_DOCUMENTO"] = pd.to_datetime(df["DATA_EMISSAO_DOCUMENTO"])
    df["CEP_2_DIG"] = df["CEP_2_DIG"].astype("category")

    # Título e introdução
    st.title("Case Previsão de Inadimplência")

    st.markdown(
        """Visão exploratória da base de dados após todas as etapas de tratamento e preparação."""
    )

    # KPIs principais
    col1, col2 = st.columns(2)
    col1.metric("Total de Registros", f"{df.shape[0]:,}")
    col2.metric("Clientes Únicos", f"{df['ID_CLIENTE'].nunique():,}")
    col1, col2 = st.columns(2)

    # col1.metric("% Inadimplentes", f"{df['TARGET_INADIMPLENCIA'].mean()*100:.2f}%")
    st.metric(
        "Período da emissão dos documentos:",
        f"{df['DATA_EMISSAO_DOCUMENTO'].min().strftime('%d/%m/%Y')} a {df['DATA_EMISSAO_DOCUMENTO'].max().strftime('%d/%m/%Y')}",
    )

    st.markdown("---")

    # Calcula as quantidades
    inadimplentes = (df["TARGET_INADIMPLENCIA"] == 1).sum()
    adimplentes = (df["TARGET_INADIMPLENCIA"] == 0).sum()

    # Cria o DataFrame de resumo
    dados_pizza = pd.DataFrame(
        {
            "Status": ["Adimplentes", "Inadimplentes"],
            "Quantidade": [adimplentes, inadimplentes],
        }
    )

    # Gera o gráfico de pizza
    fig = px.pie(
        dados_pizza,
        names="Status",
        values="Quantidade",
        title="Perceuntual de Inadimplência",
        hole=0.4,  # se quiser formato de doughnut
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Inadimplência por Categoria")

    # Seleção da variável categórica
    variavel_cat = st.selectbox(
        "Escolha uma variável categórica:",
        ["SEGMENTO_INDUSTRIAL", "PORTE", "DOMINIO_EMAIL", "FLAG_PF", "CEP_2_DIG"],
    )

    # Garante que os dados estão carregados e a variável existe
    if variavel_cat in df.columns:

        # Filtra a base, se necessário (ajuste df_filtrado conforme sua lógica)
        df_filtrado = df.copy()  # ou mantenha seu df_filtrado anterior

        df_filtrado["FLAG_PF"] = df_filtrado["FLAG_PF"].map(
            {1: "Pessoa Física", 0: "Pessoa Jurídica"}
        )

        # Calcula a taxa média de inadimplência por categoria
        inadimplencia_cat = (
            df_filtrado.groupby(variavel_cat)["TARGET_INADIMPLENCIA"]
            .mean()
            .reset_index()
            .sort_values(by="TARGET_INADIMPLENCIA", ascending=False)
        )

        # Cria o gráfico de barras horizontal
        fig_cat = px.bar(
            inadimplencia_cat,
            x="TARGET_INADIMPLENCIA",
            y=variavel_cat,
            orientation="h",
            labels={"TARGET_INADIMPLENCIA": "Taxa de Inadimplência"},
            title=f"Taxa de Inadimplência por {variavel_cat}",
        )

        # Exibe o gráfico
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.warning("A variável selecionada não está presente no DataFrame.")




    # Seleciona colunas numéricas
    numericas = df.select_dtypes(include=["int64", "float64", "int32"])

    # Remove a coluna de ID, se existir
    numericas = numericas.drop(columns=["ID_CLIENTE"], errors="ignore")

    # Calcula correlações com a variável alvo
    correlacoes = numericas.corr()["TARGET_INADIMPLENCIA"].drop("TARGET_INADIMPLENCIA")

    # Ordena por valor absoluto da correlação
    correlacoes = correlacoes.reindex(
        correlacoes.abs().sort_values(ascending=False).index
    )

    # Cria DataFrame para plotagem
    df_corr = correlacoes.reset_index()
    df_corr.columns = ["Variável", "Correlação"]

    # Gráfico de barras horizontal com Plotly
    fig = px.bar(
        df_corr,
        x="Correlação",
        y="Variável",
        orientation="h",
        title="Correlação entre as variáveis numéricas e a inadimplência",
        color="Correlação",
        color_continuous_scale="RdBu",
        range_color=[-1, 1],
    )

    fig.update_layout(
        xaxis_title="Correlação de Pearson",
        yaxis_title="Variáveis Numéricas",
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, use_container_width=True)
    


    # Agrupa por ano
    df["ANO_REF"] = df["DATA_EMISSAO_DOCUMENTO"].dt.year
    serie_anual = df.groupby("ANO_REF")["TARGET_INADIMPLENCIA"].mean().reset_index()

    # Converte ano para string (categorias)
    serie_anual["ANO_REF"] = serie_anual["ANO_REF"].astype(str)

    # Gráfico de linha com eixo categórico
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie_anual["ANO_REF"],
            y=serie_anual["TARGET_INADIMPLENCIA"],
            mode="lines+markers",
            line=dict(color="skyblue"),
            marker=dict(size=8),
            name="Taxa de Inadimplência",
        )
    )

    fig.update_layout(
        title="Evolução Anual da Taxa de Inadimplência",
        xaxis_title="Ano",
        yaxis_title="Taxa de Inadimplência",
        xaxis=dict(type="category"),
        yaxis_tickformat=".1%",
        template="plotly_dark",  # ou remova se estiver usando outro tema
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Amostras da Tabela de dados")
    st.dataframe(df.head(100))

    st.markdown("---")
    
    st.subheader("Desempenho dos modelos candidatos")

    # Abrindo e carregando o conteúdo
    with open('./data/processed/resultados_grid_search_cv.pkl', 'rb') as arquivo:
        objeto = pickle.load(arquivo)

    if arquivo:

        resultados = objeto

        # --- Seleção de modelo ---
        modelo_escolhido = st.selectbox("Selecione o modelo:", list(resultados.keys()))
        dados = resultados[modelo_escolhido]

        # --- Exibe os melhores parâmetros ---
        # st.subheader("Melhores Parâmetros")
        # st.json(dados['Melhores parâmetros'])

        # --- Exibe os scores principais ---
        st.subheader("Principais Métricas")
        col1, col2, col3 = st.columns(3)

        col1.metric("ROC AUC (Validação)", f"{dados['ROC AUC (validação)']:.4f}")
        col2.metric("ROC AUC (Teste)", f"{dados['ROC AUC (teste)']:.4f}")
        col3.metric("Acurácia", f"{dados['Classification Report']['accuracy']:.4f}")

        # --- Gráfico de métricas por classe ---
        st.subheader("Precision, Recall e F1-score por Classe")

        report = dados['Classification Report']
        classes = ['0', '1']
        metricas = ['precision', 'recall', 'f1-score']

        dados_plot = pd.DataFrame({
            'Classe': [],
            'Métrica': [],
            'Valor': []
        })

        for classe in classes:
            for metrica in metricas:
                dados_plot = pd.concat([
                    dados_plot,
                    pd.DataFrame({
                        'Classe': [classe],
                        'Métrica': [metrica],
                        'Valor': [report[classe][metrica]]
                    })
                ], ignore_index=True)

        fig_metrics = px.bar(
            dados_plot,
            x='Métrica',
            y='Valor',
            color='Classe',
            barmode='group',
            title='Métricas por Classe'
        )
        st.plotly_chart(fig_metrics, use_container_width=True)

        # --- Matriz de Confusão com Plotly ---
        st.subheader("Matriz de Confusão")

        # Extrai a matriz de confusão dos seus dados
        conf_matrix = dados['Confusion Matrix']

        # Define os rótulos dos eixos
        axis_labels = ['Classe 0', 'Classe 1']

        # Cria a figura da matriz de confusão com plotly.express
        fig_conf_plotly = px.imshow(
            conf_matrix,
            labels=dict(x="Valores Previstos", y="Valores Reais", color="Contagem"),
            x=axis_labels,
            y=axis_labels,
            text_auto=True,  # Para exibir os números dentro das células
            color_continuous_scale='Blues_r'  # Esquema de cores
        )

        # Centraliza o título e ajusta o layout
        fig_conf_plotly.update_layout(
            title_text='<b>Matriz de Confusão</b>',
            title_x=0.5
        )

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig_conf_plotly, use_container_width=True)

