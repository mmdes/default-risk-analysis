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

    st.subheader("Amostras da tabela de dados")
    st.dataframe(df.head(100))

    st.markdown("---")
    
    st.subheader("Desempenho dos modelos candidatos (em Grid Search CV)")

    # Abrindo e carregando o conteúdo
    with open('./dashboard/assets/resultados_grid_search_cv_v6.pkl', 'rb') as arquivo:
        objeto = pickle.load(arquivo)

    # Colocando os resultados do treinamento com cross validation e grid search 
    # estático pois o treinamento é demorado. Assim não será obrigatório treinar
    # com tuning de modelo e parâmetro para ter acesso a esses resultados

    resultados = {'XGBoost': {'Melhores parâmetros': {'clf__colsample_bytree': 0.6,
   'clf__gamma': 0,
   'clf__learning_rate': 0.1,
   'clf__max_depth': 10,
   'clf__min_child_weight': 1,
   'clf__n_estimators': 400,
   'clf__reg_alpha': 0.5,
   'clf__reg_lambda': 1,
   'clf__subsample': 0.8},
  'ROC AUC (validação)': 0.9614262293714677,
  'ROC AUC (teste)': 0.95959412967073,
  'Classification Report': {'0': {'precision': 0.9755051606338131,
    'recall': 0.9814259597806215,
    'f1-score': 0.9784566033609157,
    'support': 13675.0},
   '1': {'precision': 0.7462537462537463,
    'recall': 0.6891143911439115,
    'f1-score': 0.7165467625899281,
    'support': 1084.0},
   'accuracy': 0.9599566366284978,
   'macro avg': {'precision': 0.8608794534437797,
    'recall': 0.8352701754622665,
    'f1-score': 0.8475016829754218,
    'support': 14759.0},
   'weighted avg': {'precision': 0.9586673983743109,
    'recall': 0.9599566366284978,
    'f1-score': 0.9592201871134903,
    'support': 14759.0}},
  'Confusion Matrix': [[13421, 254], [337, 747]]},
 'RandomForest': {'Melhores parâmetros': {'clf__bootstrap': False,
   'clf__max_depth': 20,
   'clf__max_features': 'sqrt',
   'clf__min_samples_leaf': 1,
   'clf__min_samples_split': 5,
   'clf__n_estimators': 300},
  'ROC AUC (validação)': 0.9617971360742456,
  'ROC AUC (teste)': 0.962140929727396,
  'Classification Report': {'0': {'precision': 0.9807649789962415,
    'recall': 0.973162705667276,
    'f1-score': 0.976949053002496,
    'support': 13675.0},
   '1': {'precision': 0.6915966386554622,
    'recall': 0.7592250922509225,
    'f1-score': 0.723834652594547,
    'support': 1084.0},
   'accuracy': 0.9574496917135308,
   'macro avg': {'precision': 0.8361808088258518,
    'recall': 0.8661938989590993,
    'f1-score': 0.8503918527985215,
    'support': 14759.0},
   'weighted avg': {'precision': 0.9595265156227472,
    'recall': 0.9574496917135308,
    'f1-score': 0.9583586329169742,
    'support': 14759.0}},
  'Confusion Matrix': [[13308, 367], [261, 823]]},
 'LogisticRegression': {'Melhores parâmetros': {'clf__C': 100.0},
  'ROC AUC (validação)': 0.8665501989874699,
  'ROC AUC (teste)': 0.8681612552871416,
  'Classification Report': {'0': {'precision': 0.9775204359673024,
    'recall': 0.8394881170018281,
    'f1-score': 0.9032613399425626,
    'support': 13675.0},
   '1': {'precision': 0.27197346600331673,
    'recall': 0.7564575645756457,
    'f1-score': 0.4000975847767748,
    'support': 1084.0},
   'accuracy': 0.8333897960566434,
   'macro avg': {'precision': 0.6247469509853096,
    'recall': 0.797972840788737,
    'f1-score': 0.6516794623596687,
    'support': 14759.0},
   'weighted avg': {'precision': 0.9257003319330888,
    'recall': 0.8333897960566434,
    'f1-score': 0.8663056172919961,
    'support': 14759.0}},
  'Confusion Matrix': [[11480, 2195], [264, 820]]},
 'LightGBM': {'Melhores parâmetros': {'clf__colsample_bytree': 0.6,
   'clf__learning_rate': 0.1,
   'clf__min_child_samples': 50,
   'clf__n_estimators': 200,
   'clf__num_leaves': 100,
   'clf__subsample': 0.6},
  'ROC AUC (validação)': 0.9590157460213717,
  'ROC AUC (teste)': 0.9577255678406876,
  'Classification Report': {'0': {'precision': 0.9750835391544385,
    'recall': 0.9815722120658136,
    'f1-score': 0.9783171167231515,
    'support': 13675.0},
   '1': {'precision': 0.7462235649546828,
    'recall': 0.683579335793358,
    'f1-score': 0.7135291285507944,
    'support': 1084.0},
   'accuracy': 0.9596856155566095,
   'macro avg': {'precision': 0.8606535520545606,
    'recall': 0.8325757739295858,
    'f1-score': 0.845923122636973,
    'support': 14759.0},
   'weighted avg': {'precision': 0.9582745268885305,
    'recall': 0.9596856155566095,
    'f1-score': 0.958869310016814,
    'support': 14759.0}},
  'Confusion Matrix': [[13423, 252], [343, 741]]}}



        # --- Seleção de modelo ---
    modelo_escolhido = st.selectbox("Selecione o modelo:", list(resultados.keys()))
    dados = resultados[modelo_escolhido]

        # --- Exibe os melhores parâmetros ---
        # st.subheader("Melhores Parâmetros")
        # st.json(dados['Melhores parâmetros'])

        # --- Exibe os scores principais ---
        #st.subheader("Principais Métricas")
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
    st.subheader("Matriz de confusão")

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

    st.markdown("---")
    
    st.subheader("Desempenho do modelo vencedor Random Forest (em hold-out)")

    # Carrega os resultados do hold-out
    with open('./data/processed/resultados_holdout_random_forest.pkl', 'rb') as arquivo:
        dados_holdout = pickle.load(arquivo)

    if dados_holdout:
        # --- Exibe os scores principais ---
        #st.subheader("Principais Métricas - Hold-Out")
        col1, col2, col3 = st.columns(3)
        col1.metric("ROC AUC", f"{dados_holdout['ROC AUC']:.4f}")
        col2.metric("Acurácia", f"{dados_holdout['Acurácia']:.4f}")
        col3.metric("F1-Score (Classe 1)", f"{dados_holdout['F1-Score (Classe 1)']:.4f}")

        # --- Gráfico de métricas por classe ---
        st.subheader("Precision, Recall e F1-score por Classe")

        metricas = ['Precisão (Classe 1)', 'Recall (Classe 1)', 'F1-Score (Classe 1)']
        valores = [dados_holdout['Precisão (Classe 1)'],
                   dados_holdout['Recall (Classe 1)'],
                   dados_holdout['F1-Score (Classe 1)']]

        df_metricas = pd.DataFrame({
            'Métrica': ['Precision', 'Recall', 'F1-score'],
            'Valor': valores,
            'Classe': ['1'] * 3
        })

        fig_bar = px.bar(
            df_metricas,
            x='Métrica',
            y='Valor',
            color='Classe',
            barmode='group',
            title='Métricas por Classe (Classe 1)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Matriz de Confusão ---
        st.subheader("Matriz de Confusão")

        conf_matrix = dados_holdout['Confusion Matrix']
        labels = ['Classe 0', 'Classe 1']

        fig_conf = px.imshow(
            conf_matrix,
            labels=dict(x="Valores Previstos", y="Valores Reais", color="Contagem"),
            x=labels,
            y=labels,
            text_auto=True,
            color_continuous_scale='Blues_r'
        )
        fig_conf.update_layout(title_text="<b>Matriz de Confusão</b>", title_x=0.5)
        st.plotly_chart(fig_conf, use_container_width=True)

        
        report_str = dados_holdout['Classification_report']

        linhas = report_str.strip().split('\n')
        colunas = linhas[0].strip().split()

        linhas_dados = []
        indices = []

        for linha in linhas[1:]:
            if linha.strip() == "":
                continue
            partes = linha.strip().split()

            # Caso especial: linha de "accuracy" tem apenas 2 valores, pula ou trata separadamente
            if partes[0] == "accuracy":
                continue
            
            # Linhas com índice composto, tipo "macro avg" ou "weighted avg"
            if not partes[0].isdigit() and len(partes) > 5:
                nome = " ".join(partes[:-4])
                valores = partes[-4:]
            else:
                nome = partes[0]
                valores = partes[1:5]

            try:
                valores_float = list(map(float, valores))
                indices.append(nome)
                linhas_dados.append(valores_float)
            except ValueError:
                continue  # Pula qualquer linha mal formatada
            
        df_report = pd.DataFrame(linhas_dados, columns=colunas, index=indices)

        # Exibe com formatação no Streamlit
        st.subheader("Relatório de classificação estruturado")
        st.dataframe(df_report.style.format("{:.4f}").background_gradient(cmap='Blues'))