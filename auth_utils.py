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
            age = st.number_input("Quantos anos você tem?", min_value=18, max_value=120, step=1)
            gender = st.selectbox(
                "Qual o seu gênero?",
                [
                    "Masculino",
                    "Feminino",
                    "Não-binário",
                    "Prefiro não responder",
                    "Outro",
                ],
            )
            education = st.selectbox(
                "Qual o seu nível de escolaridade?",
                [
                    "Fundamental incompleto",
                    "Fundamental completo",
                    "Médio incompleto",
                    "Médio completo",
                    "Superior incompleto",
                    "Superior completo",
                    "Pós-graduação",
                    "Mestrado",
                    "Doutorado",
                ],
            )
            reads = st.checkbox("Você costuma ler notícias financeiras?")
            invests = st.checkbox("Você costuma investir?")
            submitted = st.form_submit_button("Confirmar Cadastro")
            if submitted:
                user_id = create_user(email, age, gender, education, reads, invests)
                st.success("Cadastro concluído!")
                return user_id
            st.stop()
    return user["id"]


def sidebar_login_info():
    """Exibe informações do usuário logado e opção de logout."""
    if st.user.is_logged_in:
        st.sidebar.write(f"Logado como {st.user.name or ''} ({st.user.email})")
        st.sidebar.caption(
            "Seu nome e email são usados apenas para login. Somente suas respostas aos formulários comporão o dataset."
        )
        if st.sidebar.button("Sair"):
            st.logout()
