import streamlit as st
import textwrap


def show():
    st.image("./assets/logo.png")
    st.title("Case Técnico - Cientista de Dados Trainee")

    texto = textwrap.dedent(
        """
        <b>Bem-vindo(a) à página inicial da aplicação!</b> Este dashboard interativo 
        foi desenvolvido como parte do case técnico para a vaga de Cientista de Dados Trainee na Datarisk. 
        O objetivo deste projeto foi desenvolver um modelo preditivo capaz de estimar a inadimplência
        de clientes com base em dados cadastrais e dados históricos mensais. Durante a preparação dos dados,
        foram aplicadas técnicas como <b>interpolação linear</b> para variáveis com tendência temporal, 
        estratégias de preenchimento como <b>backward fill</b> e <b>forward fill</b>, 
        além de <b>imputação hierárquica</b> com base em contexto, foi utilizado <b>mediana</b> e 
        <b>moda</b> conforme o tipo de variável. Também foram corrigidas <b>inconsistências temporais</b> e 
        <b>removidos registros críticos</b> para garantir a qualidade da base. Na etapa de modelagem, 
        foram testados quatro algoritmos de machine learning, sendo três deles reconhecidos por sua 
        robustez em bases desbalanceadas. Para lidar com o desbalanceamento das classes, foi testado 
        tanto a <b>técnica de oversampling</b> com <b>SMOTE</b> quanto estratégias nativas como o uso do 
        parâmetro <b>scale_pos_weight</b>. A escolha dos hiperparâmetros foi feita por meio de <b>Grid Search</b>
        com <b>validação cruzada</b>, garantindo uma busca mais eficiente por boas combinações. O modelo que 
        apresentou o melhor desempenho foi o <b>Random Forest</b>, alcançando um <b>ROC AUC de 0.96</b> e 
        <b>F1-score de 0.72</b>, <b>Recall de 0.76</b> (métrica muito importante para modelos de inadimplência) para a classe de inadimplentes 
        (Classe 1). Este dashboard reúne de forma visual e 
        interativa algumas etapas do trabalho, da análise exploratória, engenharia de atributos à avaliação dos modelos,
        com o objetivo de tornar o processo mais transparente e facilitar a interpretação dos resultados. <b>Gostaria de agradecer
         pela oportunidade de participar deste case técnico.</b> Foi uma excelente forma de aplicar conhecimentos 
        em um contexto prático e desafiador, alinhado com problemas reais enfrentados no mercado. Independentemente do 
        resultado, a experiência já representa um aprendizado valioso.
    """
    )

    # Remove quebras de linha para que o texto seja exibido corretamente
    texto = texto.replace("\n", " ")

    st.markdown(
        f"""
        <div style="text-align: justify; font-size: 16px;">
            {texto}
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .pulse {
            animation: pulse-animation 1.5s infinite;
        }

        @keyframes pulse-animation {
            0% { transform: translateX(0); opacity: 1; }
            50% { transform: translateX(5px); opacity: 0.6; }
            100% { transform: translateX(0); opacity: 1; }
        }
        </style>

        <div class="pulse" style="font-size:25px; padding: 10px 0; margin-top: 40px;">
            <span style="color: #1f77b4; font-size: 32px; margin-right: 12px;">&#8592;</span>
            <span style="vertical-align: middle;">Use a barra lateral à esquerda para navegar entre as páginas.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
