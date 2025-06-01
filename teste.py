import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

#Japa esse arquivo aqui teste autenticação do oauth ta funcionando
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

redirect_uri = 'http://localhost:8501'

authorization_endpoint = 'https://accounts.google.com/o/oauth2/auth'
token_endpoint = 'https://oauth2.googleapis.com/token'
userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'

if 'token' not in st.session_state:
    oauth = OAuth2Session(client_id, client_secret, scope='openid email profile', redirect_uri=redirect_uri)

    query_params = st.query_params

    if 'code' not in query_params:
        auth_url, state = oauth.create_authorization_url(authorization_endpoint)
        st.write(f'Por favor, [faça login clicando aqui]({auth_url})')
        st.stop()
    else:
        code = query_params['code']
        token = oauth.fetch_token(token_endpoint, code=code)
        st.session_state['token'] = token

# Com o token, pegue dados do usuário
oauth = OAuth2Session(client_id, client_secret, token=st.session_state['token'])
userinfo = oauth.get(userinfo_endpoint).json()

st.write(f'Olá, {userinfo["name"]}!')
st.write(f'Seu e-mail: {userinfo["email"]}')