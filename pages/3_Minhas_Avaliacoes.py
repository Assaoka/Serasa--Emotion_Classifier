import streamlit as st
import pandas as pd
import auth_utils
from database import get_evaluations_by_user

user_id = auth_utils.get_or_register_user()

st.title('Minhas Avaliações')

evals = get_evaluations_by_user(user_id)

if not evals:
    st.info('Você ainda não realizou avaliações.')
    st.stop()

records = []
for e in evals:
    records.append({
        'news_id': e.news_id,
        'data': e.date,
        'headline_sentiment': e.headline_sentiment,
        'headline_polarity': e.headline_polarity,
        'sentence1_sentiment': e.sentence1_sentiment,
        'sentence1_polarity': e.sentence1_polarity,
        'sentence2_sentiment': e.sentence2_sentiment,
        'sentence2_polarity': e.sentence2_polarity,
        'sentence3_sentiment': e.sentence3_sentiment,
        'sentence3_polarity': e.sentence3_polarity,
        'general_sentiment': e.general_sentiment,
        'general_polarity': e.general_polarity,
    })

df = pd.DataFrame(records)

st.dataframe(df)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Baixar CSV', csv, 'avaliacoes.csv', 'text/csv')
