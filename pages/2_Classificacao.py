import streamlit as st
import auth_utils
import pandas as pd
from database import (
    create_evaluation,
    get_news_least_classified,
    create_terms,
    get_user_by_email,
)

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info(show=False)
user_info = get_user_by_email(st.user.email)
if 'training_done' not in st.session_state:
    st.session_state.training_done = user_info.get('qnt_class', 0)
if st.session_state.get('training_done', 0) < 3:
    st.warning('Complete pelo menos 3 exemplos no treinamento antes de classificar.')
    st.stop()

DICT = dict(pd.read_csv('dictionary.csv').values)

def show_definitions(text: str):
    found = [t for t in DICT if t.lower() in text.lower()]
    for term in found:
        st.caption(f"**{term}**: {DICT[term]}")

EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo', 'Neutro']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

DESCRIPTIONS = {
    'Felicidade': 'Notícias que transmitem otimismo e celebração de resultados positivos, como lucro recorde, valorização de ações ou projeções de crescimento que evocam satisfação e bem‐estar no leitor.',
    'Tristeza': 'Notícias que destacam perdas, quedas acentuadas de mercado, cortes de dividendos ou previsões pessimistas que causam sentimento de decepção, desalento ou pesar.',
    'Nojo': 'Notícias que expressam repulsa diante de fraudes, escândalos de corrupção ou práticas abusivas em instituições financeiras, provocando aversão moral ou sensorial.',
    'Raiva': 'Notícias que comunicam injustiças, abusos de poder, alta de tarifas ou decisões políticas nocivas, gerando indignação e desejo de retaliação ou correção.',
    'Medo': 'Notícias que ressaltam riscos iminentes, crises econômicas, volatilidade extrema ou ameaças ao patrimônio, mobilizando alerta, tensão e impulso de proteção ou fuga.',
    'Surpresa': 'Notícias sobre eventos súbitos e inesperados — como choque de mercado, fusões-surpresa ou mudanças de política monetária não antecipadas — que capturam a atenção e exigem rápida reavaliação.',
    'Desprezo': 'Notícias que manifestam desdém ou escárnio em relação a empresas, gestores ou reguladores tidos como incompetentes, corruptos ou moralmente inferiores, criando sensação de superioridade crítica.',
}

with st.sidebar:
    st.header('Emoções de Ekman')
    for emo, desc in DESCRIPTIONS.items():
        st.markdown(f'**{emo}**: {desc}')

# Reset fields from previous interactions before widgets are created
if st.session_state.pop('reset_fields', False):
    for key in ['h_sent', 'h_pol', 'g_sent', 'g_pol']:
        st.session_state.pop(key, None)
    for i in range(1, 4):
        st.session_state.pop(f'sent_{i}', None)
        st.session_state.pop(f'pol_{i}', None)
    st.session_state.pop('current_news', None)
    st.session_state.pop('unknown_terms', None)

st.title("Classificação de Notícias")

if 'msg' in st.session_state:
    st.success(st.session_state.pop('msg'))

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
show_definitions(news.headline)

sentences = [news.f1, news.f2, news.f3]

def select(label, options, key):
    # Definindo o valor padrão para o selectbox a partir de session_state ou 'Não selecionado'
    default_value = st.session_state.get(key, 'Não selecionado')
    return st.selectbox(label, options=options, key=key, index=options.index(default_value))

cols = st.columns(2)
with cols[0]: headline_sent = select('Sentimento da Manchete', EMOTIONS, 'h_sent')
with cols[1]: headline_pol = select('Polaridade da Manchete', POLARITIES, 'h_pol')
st.write("---")

sentiments = []
polarities = []
for i, sent in enumerate(sentences, 1):
    st.text(f"Frase {i}: {sent}")
    show_definitions(sent)
    cols = st.columns(2)
    with cols[0]: sentiments.append(select(f'Sentimento {i}', EMOTIONS, f'sent_{i}'))
    with cols[1]: polarities.append(select(f'Polaridade {i}', POLARITIES, f'pol_{i}'))
    st.write("---")

cols = st.columns(2)
with cols[0]: general_sent = select('Sentimento Geral', EMOTIONS, 'g_sent')
with cols[1]: general_pol = select('Polaridade Geral', POLARITIES, 'g_pol')

unknown_terms = st.text_input('Termos que você não conhece (separe por vírgulas)', key='unknown_terms', value='')

def request_reset():
    """Flag that fields should be cleared on the next run."""
    st.session_state['reset_fields'] = True

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
        if unknown_terms:
            create_terms(news.id, unknown_terms.split(','))
        st.session_state.pop('current_news', None)
        st.session_state['msg'] = 'Avaliação salva!'
        request_reset()
        st.rerun()
    else:
        st.error('Preencha todos os campos antes de salvar.')

if cols[1].button('Pular Notícia', use_container_width=True):
    if unknown_terms:
        create_terms(news.id, unknown_terms.split(','))
    st.session_state.pop('current_news', None)
    request_reset()
    st.rerun()
