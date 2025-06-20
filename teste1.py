import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

st.set_page_config(page_title="Login com Google", page_icon="🔐")

st.title("🔐 Autenticação com Google")

# Carregando variáveis do secrets.toml
client_id = st.secrets["auth_google"]["client_id"]
client_secret = st.secrets["auth_google"]["client_secret"]
redirect_uri = st.secrets["auth"]["redirect_uri"]

# Endpoints do Google OAuth
authorization_endpoint = "https://accounts.google.com/o/oauth2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"

# Sessão OAuth
oauth = OAuth2Session(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="openid email profile"
)

# Cria URL de autenticação
auth_url, state = oauth.create_authorization_url(authorization_endpoint)

# Mostra botão de login
if "token" not in st.session_state:
    st.markdown(f"[👉 Clique aqui para fazer login com o Google]({auth_url})")

    # ✅ Substituição feita aqui:
    code = st.query_params.get("code")
    if code:
        token = oauth.fetch_token(token_endpoint, code=code)
        st.session_state["token"] = token

# Após login, exibe dados do usuário
if "token" in st.session_state:
    userinfo = oauth.get(userinfo_endpoint).json()
    st.success(f"✅ Login realizado com sucesso, {userinfo['name']}!")
    st.image(userinfo["picture"], width=100, caption="Foto de perfil")
    st.write("**Email:**", userinfo["email"])
    st.write("**ID Google:**", userinfo["sub"])
    st.write("**Dados completos:**")
    st.json(userinfo)
