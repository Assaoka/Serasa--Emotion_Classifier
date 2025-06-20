import streamlit as st

st.title("Autenticação")


if not st.user.is_logged_in:
    if st.button("Autenticar"):
        st.login("auth_google")

# Exibe dados do usuário autenticado
st.json(st.user)