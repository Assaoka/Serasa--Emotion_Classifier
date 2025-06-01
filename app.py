import streamlit as st
from database import init, create_user, create_evaluation, get_random_news_with_three_sentences
#from database import create_news

# Configuração inicial do Streamlit
st.set_page_config(page_title="Emotion Classifier", layout="wide")

# Recupera a URL do banco a partir dos segredos do Streamlit e inicializa o DB
DATABASE_URL = st.secrets["postgres"]
init(DATABASE_URL)

# Mapeamentos de opções para inteiros
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

# Login via email
if 'user_id' not in st.session_state:
    st.sidebar.header("Login")
    email_input = st.sidebar.text_input("Digite seu email para acessar:")
    if st.sidebar.button("Entrar"):
        if email_input and "@" in email_input:
            user_id = create_user(email_input)
            st.session_state['user_id'] = user_id
            # Ao logar, carrega uma notícia e armazena em sessão
            news_item = get_random_news_with_three_sentences()
            if news_item:
                st.session_state['news_id'] = news_item.id
                st.session_state['news_headline'] = news_item.headline
                st.session_state['news_summary'] = news_item.summary
            st.success("Usuário autenticado com sucesso!")
        else:
            st.sidebar.error("Insira um email válido.")
    st.stop()

# Usuário logado
user_id = st.session_state['user_id']
st.write(f"Bem-vindo, usuário ID {user_id}!")

# Carrega notícia da sessão ou, se não existir, captura nova
if 'news_id' not in st.session_state:
    news_item = get_random_news_with_three_sentences()
    if not news_item:
        st.error("Não há notícias com resumo contendo exatamente 3 frases.")
        st.stop()
    st.session_state['news_id'] = news_item.id
    st.session_state['news_headline'] = news_item.headline
    st.session_state['news_summary'] = news_item.summary

# Recupera detalhes da notícia atual da sessão
current_news_id = st.session_state['news_id']
current_headline = st.session_state['news_headline']
current_summary = st.session_state['news_summary']

# Exibe manchete atual
st.header(current_headline)

# Divide o resumo em 3 frases
sentences = current_summary.split('. ')
sentences = [s if s.endswith('.') else s + '.' for s in sentences]

# Coleta classificações
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
