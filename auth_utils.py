import streamlit as st
from database import init, create_user, get_user_by_email

# Inicializa conexão com o banco ao importar
DATABASE_URL = st.secrets["auth"]["postgres"]
init(DATABASE_URL)


def ensure_logged_in():
    """Garante que o usuário esteja autenticado via Auth0."""
    if not st.user.is_logged_in:
        st.info("Você não está autenticado.")
        if st.button("Entrar com Auth0"):
            st.login("auth0")
        st.stop()


def get_or_register_user() -> int:
    """Retorna o ID do usuário logado ou solicita cadastro."""
    ensure_logged_in()

    userinfo = st.user
    email = userinfo.email
    if not email:
        st.error("Não foi possível obter o email do usuário.")
        st.logout()
        st.stop()

    user = get_user_by_email(email)
    if user is None:
        st.header("Primeiro acesso - complete seu cadastro")
        with st.form("user_registration_form"):
            age = st.number_input("Quantos anos você tem?", min_value=1, max_value=120, step=1)
            gender = st.selectbox("Qual o seu gênero?", ["Masculino", "Feminino", "Outro"])
            education = st.selectbox(
                "Qual o seu nível de escolaridade?",
                [
                    "Ensino Fundamental",
                    "Ensino Médio",
                    "Superior",
                    "Pós-graduação",
                    "Mestrado",
                    "Doutorado",
                    "Outro",
                ],
            )
            submitted = st.form_submit_button("Confirmar Cadastro")
            if submitted:
                user_id = create_user(email, age, gender, education)
                st.success("Cadastro concluído!")
                return user_id
            st.stop()
    return user["id"]
