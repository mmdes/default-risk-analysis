import streamlit as st
from pages import inicio, sistema_risk_predict, eda


def main():
    # Configurar o título da página e o ícone
    st.set_page_config(
        page_title="Risk Predictor",
        page_icon="./assets/mini-logo.png",
        initial_sidebar_state="expanded",
    )

    hide_streamlit_style = """
        <style>
        /* Menu hamburguer padrão */
        #MainMenu {visibility: hidden;}
        /* Rodapé “Made with Streamlit” */
        footer {visibility: hidden;}
        /* Cabeçalho interno, se existir */
        header {visibility: hidden;}
        /* Botão “Deploy” no topo */
        .stDeployButton {display: none;}
        /* Container de decoração (engloba o texto “Deploy” + menu de três pontos) */
        #stDecoration {display: none;}

        /* --- ADICIONADO AQUI --- */
        /* Esconde o botão de expandir/recolher a barra lateral (a "double arrow") */
        [data-testid="stSidebarCollapseButton"] {
            display: none;
        }
        /* --- FIM DA ADIÇÃO --- */

        /* Ajuste de margem para subir seu conteúdo ao topo */
        .reportview-container {margin-top: -2em;}
        [data-testid="stSidebarNav"] { display: none; } 
         [data-testid="stSidebar"] {
        background: linear-gradient(
            to bottom,
            #ffffff 0%,    /* branco no topo */
            #555555 35%,   /* cinza médio já em 20% */
            #0A0A0A 100%
        ) !important;
        }
        /* Garante que o gradiente cubra toda a altura */
        [data-testid="stSidebar"] > div {
            height: 100vh;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
   


    # Criação da barra lateral para navegação
    st.sidebar.image("./assets/logo.png", use_container_width=True)
    st.sidebar.title("Navegação")
    pagina_selecionada = st.sidebar.selectbox(
        "Selecione uma página:",
        ["Início", "Dashboard", "Sistema Risk Predictor"],
    )

    # Renderizar a página selecionada
    if pagina_selecionada == "Início":
        inicio.show()
    elif pagina_selecionada == "Dashboard":
        eda.show()
    elif pagina_selecionada == "Sistema Risk Predictor":
        sistema_risk_predict.show()


# -----------------------------------------------------------------------------
# PONTO DE ENTRADA PRINCIPAL
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    main()
