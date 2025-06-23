import streamlit as st
import auth_utils
from database import (
    create_evaluation,
    get_news_least_classified,
)

EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

user_id = auth_utils.get_or_register_user()

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

st.header(news.headline)

sentences = [s if s.endswith('.') else s + '.' for s in news.summary.split('. ')]

def select(label, options, key):
    return st.selectbox(label, options=options, key=key)

headline_sent = select('Sentimento da Manchete', EMOTIONS, 'h_sent')
headline_pol = select('Polaridade da Manchete', POLARITIES, 'h_pol')

sentiments = []
polarities = []
for i, sent in enumerate(sentences, 1):
    st.write(f"**Frase {i}:** {sent}")
    sentiments.append(select(f'Sentimento {i}', EMOTIONS, f'sent_{i}'))
    polarities.append(select(f'Polaridade {i}', POLARITIES, f'pol_{i}'))

general_sent = select('Sentimento Geral', EMOTIONS, 'g_sent')
general_pol = select('Polaridade Geral', POLARITIES, 'g_pol')

if st.button('Salvar Avaliação'):
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
        st.experimental_rerun()
    else:
        st.error('Preencha todos os campos antes de salvar.')

if st.button('Pular Notícia'):
    st.session_state.pop('current_news', None)
    st.experimental_rerun()
