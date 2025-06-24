import streamlit as st
import auth_utils
from database import (
    create_evaluation,
    get_news_least_classified,
)

EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo', 'Neutro']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info()
if st.session_state.get('training_done', 0) < -1:
    st.warning('Complete pelo menos 3 exemplos no treinamento antes de classificar.')
    st.stop()

st.title("Classificação de Notícias")

if 'current_news' not in st.session_state:
    news_item = get_news_least_classified(user_id)
    if news_item:
        st.session_state['current_news'] = news_item
    else:
        st.info('Não há notícias disponíveis para classificação.')

news = st.session_state.get('current_news')
if not news:
    st.stop()

st.subheader(news.headline)

sentences = [news.f1, news.f2, news.f3]

def select(label, options, key):
    return st.selectbox(label, options=options, key=key)

cols = st.columns(2)
with cols[0]: headline_sent = select('Sentimento da Manchete', EMOTIONS, 'h_sent')
with cols[1]: headline_pol = select('Polaridade da Manchete', POLARITIES, 'h_pol')
st.write("---")

sentiments = []
polarities = []
for i, sent in enumerate(sentences, 1):
    st.text(f"Frase {i}: {sent}")
    cols = st.columns(2)
    with cols[0]: sentiments.append(select(f'Sentimento {i}', EMOTIONS, f'sent_{i}'))
    with cols[1]: polarities.append(select(f'Polaridade {i}', POLARITIES, f'pol_{i}'))
    st.write("---")

cols = st.columns(2)
with cols[0]: general_sent = select('Sentimento Geral', EMOTIONS, 'g_sent')
with cols[1]: general_pol = select('Polaridade Geral', POLARITIES, 'g_pol')

def zerar_campos():
    st.session_state['h_sent'] = 'Não selecionado'
    st.session_state['h_pol'] = 'Não selecionado'
    for i in range(1, 4):
        st.session_state[f'sent_{i}'] = 'Não selecionado'
        st.session_state[f'pol_{i}'] = 'Não selecionado'
    st.session_state['g_sent'] = 'Não selecionado'
    st.session_state['g_pol'] = 'Não selecionado'
    
cols = st.columns(2)
if cols[0].button('Salvar Avaliação', use_container_width=True):
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
        for key in list(st.session_state.keys()):
            if key.startswith(('h_', 'g_', 'sent_', 'pol_')):
                del st.session_state[key]
        st.session_state.pop('current_news')
        st.success('Avaliação salva!')
        zerar_campos()
        st.rerun()
    else:
        st.error('Preencha todos os campos antes de salvar.')

if cols[1].button('Pular Notícia', use_container_width=True):
    st.session_state.pop('current_news', None)
    zerar_campos()
    st.rerun()
