import streamlit as st
import pandas as pd
import auth_utils

EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo', 'Neutro']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

DESCRIPTIONS = {
    'Felicidade': 'Alegria, satisfação ou bem-estar',
    'Tristeza': 'Sentimento de perda ou desânimo',
    'Nojo': 'Repulsa ou aversão',
    'Raiva': 'Irritação ou hostilidade',
    'Medo': 'Apreensão diante de uma ameaça',
    'Surpresa': 'Reação ao inesperado',
    'Desprezo': 'Sentimento de superioridade ou desdém',
}

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info()

st.title('Treinamento')

if 'training_data' not in st.session_state:
    df = pd.read_csv('training_samples.csv')
    st.session_state.training_data = df.sample(frac=1).reset_index(drop=True)
    st.session_state.training_index = 0
    st.session_state.training_done = 0

with st.sidebar:
    st.header('Emoções de Ekman')
    for emo, desc in DESCRIPTIONS.items():
        st.markdown(f'**{emo}**: {desc}')

data = st.session_state.training_data
idx = st.session_state.training_index
row = data.iloc[idx]

st.subheader(row['manchete'])

sentences = [row['f1'], row['f2'], row['f3']]

cols = st.columns(2)
with cols[0]:
    h_sent = st.selectbox('Sentimento da Manchete', EMOTIONS, key='t_h_sent')
with cols[1]:
    h_pol = st.selectbox('Polaridade da Manchete', POLARITIES, key='t_h_pol')

st.write('---')

sentiments = []
polarities = []
for i, sent in enumerate(sentences, 1):
    st.text(f'Frase {i}: {sent}')
    cols = st.columns(2)
    with cols[0]:
        sentiments.append(st.selectbox(f'Sentimento {i}', EMOTIONS, key=f't_s{i}'))
    with cols[1]:
        polarities.append(st.selectbox(f'Polaridade {i}', POLARITIES, key=f't_p{i}'))
    st.write('---')

cols = st.columns(2)
with cols[0]:
    g_sent = st.selectbox('Sentimento Geral', EMOTIONS, key='t_g_sent')
with cols[1]:
    g_pol = st.selectbox('Polaridade Geral', POLARITIES, key='t_g_pol')

cols = st.columns(2)
if cols[0].button('Salvar Resposta', use_container_width=True):
    values = [h_sent, h_pol, g_sent, g_pol] + sentiments + polarities
    if all(v != 'Não selecionado' for v in values):
        
        st.session_state.training_done += 1
        for k in list(st.session_state.keys()):
            if k.startswith('t_'):
                del st.session_state[k]
        if st.session_state.training_index < len(data) - 1:
            st.session_state.training_index += 1
            st.rerun()
        else:
            st.success('Treinamento finalizado.')
            st.session_state.training_index = 0
    else:
        st.error('Preencha todos os campos antes de salvar.')
if cols[1].button('Pular Notícia', use_container_width=True):
    if st.session_state.training_index < len(data) - 1:
        st.session_state.training_index += 1
        st.rerun()
    else:
        st.session_state.training_index = 0
