import streamlit as st

st.set_page_config(page_title="Login Test")

st.title("🔐 Teste de Autenticação")

if not st.user.is_logged_in:
    st.info("Você não está autenticado.")
    if st.button("Autenticar com Auth0"):
        st.login("auth0")
    st.stop()

st.success(f"Bem-vindo, {st.user.name or 'usuário'}!")
st.json(st.user)