import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from database import init, create_user, create_evaluation, get_random_news_with_three_sentences, email_exists, register_user_with_questions, get_user_by_email

# Credenciais
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

DATABASE_URL = st.secrets["postgres"]
init(DATABASE_URL)

# Ambiente local:
# redirect_uri = 'http://localhost:8501'

# Quando estamos no local público:
redirect_uri = 'https://serasa--emotionclassifier-bxg6zimdlwweszk4euow7z.streamlit.app/'
authorization_endpoint = 'https://accounts.google.com/o/oauth2/auth'
token_endpoint = 'https://oauth2.googleapis.com/token'
userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'

EMOTIONS = ['Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo']
POLARITIES = ['Positivo', 'Neutro', 'Negativo']

# Função auxiliar para exibir controles de classificação e retornar inteiros

def show_classification_controls(label: str, key_prefix: str):
    st.subheader(label)
    col1, col2 = st.columns(2)
    with col1:
        selected_sent = st.selectbox("Sentimento", options=EMOTIONS, key=f"sent_{key_prefix}")
        sent_value = EMOTIONS.index(selected_sent) + 1
    with col2:
        selected_pol = st.selectbox("Polaridade", options=POLARITIES, key=f"pol_{key_prefix}")
        pol_value = POLARITIES.index(selected_pol) + 1
    return sent_value, pol_value

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

    # Buscar o usuário e pegar seu ID (user_id)
    user = get_user_by_email(userinfo["email"])

    if user:
        user_id = user["id"]  # Pegamos o user_id do banco de dados
        st.session_state['user_id'] = user_id

        # Carrega notícia da sessão ou captura nova
        if 'news_id' not in st.session_state:
            news_item = get_random_news_with_three_sentences()
            if not news_item:
                st.error("Não há notícias com resumo contendo exatamente 3 frases.")
                st.stop()
            st.session_state['news_id'] = news_item.id
            st.session_state['news_headline'] = news_item.headline
            st.session_state['news_summary'] = news_item.summary

        # Recupera detalhes da notícia atual
        current_news_id = st.session_state['news_id']
        current_headline = st.session_state['news_headline']
        current_summary = st.session_state['news_summary']

        # Exibe a manchete
        st.header(current_headline)

        # Divide o resumo em 3 frases
        sentences = current_summary.split('. ')
        sentences = [s if s.endswith('.') else s + '.' for s in sentences]

        # Coleta as classificações
        evals = {}

        # Manchete
        headline_sent, headline_pol = show_classification_controls("Classifique a Manchete:", "headline")
        evals['headline_sentiment'] = headline_sent
        evals['headline_polarity'] = headline_pol

        # Frases do resumo
        sentence_sentiments = []
        sentence_polarities = []
        for idx, sentence in enumerate(sentences, start=1):
            st.write(f"**Frase {idx}:** {sentence}")
            sent_val, pol_val = show_classification_controls(f"Frase {idx}", f"sent_{idx}")
            sentence_sentiments.append(sent_val)
            sentence_polarities.append(pol_val)

        # Classificação geral
        general_sent, general_pol = show_classification_controls("Classificação Geral:", "general")
        evals['general_sentiment'] = general_sent
        evals['general_polarity'] = general_pol

        # Botão para salvar avaliação
        def save_and_next():
            create_evaluation(
                user_id=user_id,
                news_id=current_news_id,
                headline_sentiment=evals['headline_sentiment'],
                headline_polarity=evals['headline_polarity'],
                sentence_sentiments=sentence_sentiments,
                sentence_polarities=sentence_polarities,
                general_sentiment=evals['general_sentiment'],
                general_polarity=evals['general_polarity']
            )
            # Após salvar, carrega nova notícia
            next_news = get_random_news_with_three_sentences()
            if next_news:
                st.session_state['news_id'] = next_news.id
                st.session_state['news_headline'] = next_news.headline
                st.session_state['news_summary'] = next_news.summary
            st.rerun()

        if st.button("Salvar Avaliação"):
            save_and_next()

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