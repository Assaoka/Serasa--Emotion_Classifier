import streamlit as st

st.set_page_config(
    page_title="Anotação de Sentimentos em Notícias Financeiras",
    page_icon= "src/img/unifesp_icon.ico",
)

st.html('''
<style>
    #MainMenu {visibility: collapsed;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
</style>''')

import auth_utils
user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info()

st.sidebar.success("Selecione uma página acima")

pg = st.navigation([
    st.Page("pages/0_Home.py", title="Home", icon="🏠"),
    st.Page("pages/1_Treinamento.py", title="Treinamento", icon="📚"),
    st.Page("pages/2_Classificacao.py", title="Classificação", icon="📊"),
    st.Page("pages/3_Minhas_Avaliacoes.py", title="Minhas Avaliações", icon="📋"),
])
pg.run()
