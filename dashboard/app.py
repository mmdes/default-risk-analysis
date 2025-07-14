import streamlit as st
from pages import inicio, sistema_risk_predict, eda


def main():
    # Configurar o título da página e o ícone
    st.set_page_config(
        page_title="Risk Predict",
        page_icon="./dashboard/assets/mini-logo.png",
        initial_sidebar_state="expanded",
    )

    # Injeção de css
    hide_streamlit_style = """
    <style>
    /* Esconde menus e marca d'água do Streamlit */
    #MainMenu, footer, header, .stDeployButton, #stDecoration {
        display: none;
    }

     /* Esconde o botão "Deploy" isolado */
    [data-testid="stDeployButton"] {
        display: none !important;
    }

    /* Esconde o botão de status com "File change. Rerun..." */
    [data-testid="stStatusWidget"] {
        display: none;
    }

   

    /* Esconde lista de páginas automática e linha acima da logo */
    [data-testid="stSidebarNav"] ul, 
    [data-testid="stSidebarNav"] hr {
        display: none;
    }

    /* Personaliza o fundo da barra lateral */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            to bottom,
            #ffffff 0%,
            #555555 35%,
            #0A0A0A 100%
        ) !important;
    }
    </style>
    """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Criação da barra lateral para navegação
    st.sidebar.image("./dashboard/assets/logo.png", use_container_width=True)
    st.sidebar.title("Navegação")
    pagina_selecionada = st.sidebar.selectbox(
        "Selecione uma página:",
        ["Início", "Dashboard", "Sistema Risk Predict"],
    )

    # Renderizar a página selecionada
    if pagina_selecionada == "Início":
        inicio.show()
    elif pagina_selecionada == "Dashboard":
        eda.show()
    elif pagina_selecionada == "Sistema Risk Predict":
        sistema_risk_predict.show()


# -----------------------------------------------------------------------------
# PONTO DE ENTRADA PRINCIPAL
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    main()
