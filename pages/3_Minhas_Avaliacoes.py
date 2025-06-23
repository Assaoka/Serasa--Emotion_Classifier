import streamlit as st
import pandas as pd
import auth_utils
from database import get_evaluations_by_user

EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info()

st.title('Minhas Avaliações')

evals = get_evaluations_by_user(user_id)

if not evals:
    st.info('Você ainda não realizou avaliações.')
    st.stop()

records = []
for e in evals:
    sentences = [s if s.endswith('.') else s + '.' for s in e.news.summary.split('. ')][:3]
    records.append({
        'data': e.date,
        'manchete': e.news.headline,
        'frase1': sentences[0] if len(sentences) > 0 else '',
        'frase2': sentences[1] if len(sentences) > 1 else '',
        'frase3': sentences[2] if len(sentences) > 2 else '',
        'sent_manchete': EMOTIONS[e.headline_sentiment],
        'pol_manchete': POLARITIES[e.headline_polarity],
        'sent1': EMOTIONS[e.sentence1_sentiment],
        'pol1': POLARITIES[e.sentence1_polarity],
        'sent2': EMOTIONS[e.sentence2_sentiment],
        'pol2': POLARITIES[e.sentence2_polarity],
        'sent3': EMOTIONS[e.sentence3_sentiment],
        'pol3': POLARITIES[e.sentence3_polarity],
        'sent_geral': EMOTIONS[e.general_sentiment],
        'pol_geral': POLARITIES[e.general_polarity],
    })

df = pd.DataFrame(records)

st.dataframe(df)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Baixar CSV', csv, 'avaliacoes.csv', 'text/csv')
