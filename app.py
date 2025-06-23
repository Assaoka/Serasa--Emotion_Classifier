import streamlit as st
import auth_utils

st.set_page_config(page_title="Classificador de Notícias")

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info()

st.sidebar.success("Selecione uma página acima")

st.title("Classificador de Notícias Financeiras")
st.write(
    "Utilize o menu lateral para acessar o treinamento, realizar classificações ou visualizar suas avaliações."
)
