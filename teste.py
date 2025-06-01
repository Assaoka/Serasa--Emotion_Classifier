import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from database import init, create_user, create_evaluation, get_random_news_with_three_sentences, email_exists, register_user_with_questions

# Credenciais
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

DATABASE_URL = st.secrets["postgres"]
init(DATABASE_URL)

redirect_uri = 'http://localhost:8501'
authorization_endpoint = 'https://accounts.google.com/o/oauth2/auth'
token_endpoint = 'https://oauth2.googleapis.com/token'
userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'

# Função para iniciar o OAuth e redirecionar para o Google
def start_google_auth_flow():
    oauth = OAuth2Session(
        client_id,
        client_secret,
        scope='openid email profile',
        redirect_uri=redirect_uri
    )
    auth_url, state = oauth.create_authorization_url(authorization_endpoint)
    st.experimental_set_query_params(state=state)  # salva o estado
    st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
    st.stop()  # para evitar execução adicional

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 3em;
    font-size: 1em;
}
</style>
""", unsafe_allow_html=True)

if 'token' in st.session_state:
    oauth = OAuth2Session(client_id, client_secret, token=st.session_state['token'])
    userinfo = oauth.get(userinfo_endpoint).json()

    with st.sidebar:
        st.header("Usuário Autenticado")
        st.write(f"👤 {userinfo['name']}")
        st.write(f"✉️ {userinfo['email']}")

    st.write(f'Olá, {userinfo["name"]}!')
    st.write(f'Seu e-mail autenticado: {userinfo["email"]}')

    # Usa as funções do módulo database
    if email_exists(userinfo["email"]):
        st.success("Usuário já cadastrado na base!")
    else:
        st.warning("E-mail não cadastrado. Vamos te cadastrar agora!")
        register_user_with_questions(userinfo["email"])

else:
    with st.sidebar:
        st.header("Login")
        start_google_auth = st.button("Entrar com o Google")

    if start_google_auth:
        start_google_auth_flow()

    if 'code' in st.query_params:
        oauth = OAuth2Session(
            client_id,
            client_secret,
            scope='openid email profile',
            redirect_uri=redirect_uri
        )
        code = st.query_params['code']
        try:
            token = oauth.fetch_token(
                token_endpoint,
                code=code,
                redirect_uri=redirect_uri
            )
            st.session_state['token'] = token
            st.rerun()
        except Exception:
            st.error("Erro ao autenticar com o Google.")
            st.stop()