import streamlit as st
import pandas as pd
import auth_utils

def show_definitions(text: str):
    found = [t for t in DICT if t.lower() in text.lower()]
    for term in found:
        st.caption(f"**{term}**: {DICT[term]}")

DICT = dict(pd.read_csv('dictionary.csv').values)

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info(show=False)

st.title('Treinamento')

if 'training_data' not in st.session_state:
    df = pd.read_csv('training_samples.csv')
    st.session_state.training_data = df.sample(frac=1).reset_index(drop=True)
    st.session_state.training_index = 0
    st.session_state.training_done = 0


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

data = st.session_state.training_data
idx = st.session_state.training_index
row = data.iloc[idx]

if st.session_state.get('show_solution'):
    expected = st.session_state.get('expected')
    st.subheader('Gabarito')
    st.write(expected)
    if st.button('Continuar'):
        st.session_state.show_solution = False
        st.session_state.pop('expected', None)
        if st.session_state.training_index < len(data) - 1:
            st.session_state.training_index += 1
        else:
            st.success('Treinamento finalizado.')
            st.session_state.training_index = 0
        st.rerun()
    st.stop()

st.subheader(row['manchete'])
show_definitions(row['manchete'])

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
    show_definitions(sent)
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
        labels = [
            'Sentimento da Manchete',
            'Sentimento 1',
            'Sentimento 2',
            'Sentimento 3',
            'Sentimento Geral',
            'Polaridade da Manchete',
            'Polaridade 1',
            'Polaridade 2',
            'Polaridade 3',
            'Polaridade Geral',
        ]
        st.session_state.training_done += 1
        user_ans = [h_sent] + sentiments + [g_sent] + [h_pol] + polarities + [g_pol]
        expected_ans = [
            row['sent_manchete'],
            row['sent1'],
            row['sent2'],
            row['sent3'],
            row['sent_geral'],
            row['pol_manchete'],
            row['pol1'],
            row['pol2'],
            row['pol3'],
            row['pol_geral'],
        ]
        df_result = pd.DataFrame({'Sua Resposta': user_ans, 'Gabarito': expected_ans}, index=labels)
        st.session_state.expected = df_result
        st.session_state.show_solution = True
        for k in list(st.session_state.keys()):
            if k.startswith('t_'):
                del st.session_state[k]
        st.rerun()
    else:
        st.error('Preencha todos os campos antes de salvar.')
if cols[1].button('Pular Notícia', use_container_width=True):
    if st.session_state.training_index < len(data) - 1:
        st.session_state.training_index += 1
        st.session_state.show_solution = False
        st.rerun()
    else:
        st.session_state.training_index = 0
        st.session_state.show_solution = False
