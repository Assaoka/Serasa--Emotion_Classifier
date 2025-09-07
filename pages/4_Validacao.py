# validar_avaliacoes.py
import streamlit as st
import pandas as pd
import auth_utils
from database import get_user_by_email, get_news_by_id, create_evaluation, create_terms

st.title("Validação das Avaliações")

# --- LOGIN E REGISTRO ---
user_id = auth_utils.get_or_register_user()   # cria ou recupera usuário
auth_utils.sidebar_login_info(show=False)     # mostra login no sidebar

user_info = get_user_by_email(st.user.email)

# --- Configurações ---
EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo', 'Neutro']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

CSV_PATH = "avaliacoes.csv"

# ---------- Carregar CSV ----------
def _load_csv():
    return pd.read_csv(CSV_PATH)

if "df" not in st.session_state:
    st.session_state.df = _load_csv()
if "idx" not in st.session_state:
    st.session_state.idx = 0

df = st.session_state.df
if df.empty:
    st.info("O arquivo avaliacoes.csv está vazio.")
    st.stop()

# ---------- Funções utilitárias ----------
SELECT_KEYS = ["h_sent", "h_pol", "g_sent", "g_pol"] + \
              [f"sent_{i}" for i in range(1,4)] + [f"pol_{i}" for i in range(1,4)]

def reset_widget_keys():
    for k in SELECT_KEYS:
        st.session_state.pop(k, None)

def safe_code(code, maxlen):
    try:
        c = int(code)
    except Exception:
        return 0
    return c if 0 <= c < maxlen else 0

def select(label, options, key, default_idx=0):
    idx = safe_code(default_idx, len(options))
    return st.selectbox(label, options, index=idx, key=key)

def go_next():
    if st.session_state.idx < len(df) - 1:
        st.session_state.idx += 1
        reset_widget_keys()

# ---------- Linha atual do CSV ----------
row = df.iloc[st.session_state.idx]

# pega notícia do banco pelo ID do CSV (primeira coluna)
news_id = row.iloc[0]
news = get_news_by_id(news_id)

if not news:
    st.error(f"Notícia com ID {news_id} não encontrada no banco.")
    st.stop()

# ---------- Exibir notícia ----------
st.subheader(news.headline)
sentences = [news.f1, news.f2, news.f3]

# Função opcional para mostrar definições ou highlights
def show_definitions(sent):
    # aqui você pode adicionar lógica de exibição de termos desconhecidos, etc.
    pass

# ---------- Selects com defaults do CSV ----------
cols = st.columns(2)
with cols[0]: headline_sent = select('Sentimento da Manchete', EMOTIONS, 'h_sent', row.get('headline_sentiment', 0))
with cols[1]: headline_pol = select('Polaridade da Manchete', POLARITIES, 'h_pol', row.get('headline_polarity', 0))
st.write("---")

sentiments = []
polarities = []
for i, sent in enumerate(sentences, 1):
    st.text(f"Frase {i}: {sent}")
    show_definitions(sent)
    cols = st.columns(2)
    with cols[0]:
        sentiments.append(select(f'Sentimento {i}', EMOTIONS, f'sent_{i}', row.get(f'sentence{i}_sentiment', 0)))
    with cols[1]:
        polarities.append(select(f'Polaridade {i}', POLARITIES, f'pol_{i}', row.get(f'sentence{i}_polarity', 0)))
    st.write("---")

cols = st.columns(2)
with cols[0]: general_sent = select('Sentimento Geral', EMOTIONS, 'g_sent', row.get('general_sentiment', 0))
with cols[1]: general_pol = select('Polaridade Geral', POLARITIES, 'g_pol', row.get('general_polarity', 0))

st.write("---")

# ---------- Botões ----------
bcols = st.columns(2)

# Salvar avaliação no banco
if bcols[0].button("Salvar avaliação ✅", use_container_width=True):
    values = [headline_sent, headline_pol, general_sent, general_pol] + sentiments + polarities
    if all(v != 'Não selecionado' for v in values):
        create_evaluation(
            user_id=user_id,
            news_id=news.id,
            headline_sentiment=EMOTIONS.index(headline_sent),
            headline_polarity=POLARITIES.index(headline_pol),
            sentence_sentiments=[EMOTIONS.index(s) for s in sentiments],
            sentence_polarities=[POLARITIES.index(p) for p in polarities],
            general_sentiment=EMOTIONS.index(general_sent),
            general_polarity=POLARITIES.index(general_pol),
        )
        unknown_terms = row.get("unknown_terms", "")
        if unknown_terms:
            create_terms(news.id, unknown_terms.split(','))
        st.success("Avaliação enviada para o banco de dados! ✅")
        go_next()
        reset_widget_keys()
        st.rerun()
    else:
        st.error("Preencha todos os campos antes de enviar para o banco.")

# Pular
if bcols[1].button("Pular ⏭️", use_container_width=True):
    go_next()
    reset_widget_keys()
    st.rerun()
