import streamlit as st
import pandas as pd
import auth_utils
from database import get_user_by_email, update_user_qnt_class, create_terms

def show_definitions(text: str):
    found = [t for t in DICT if t.lower() in text.lower()]
    for term in found:
        st.caption(f"**{term}**: {DICT[term]}")

DICT = dict(pd.read_csv('dictionary.csv').values)

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info(show=False)
user_info = get_user_by_email(st.user.email)

st.title('Treinamento')

if 'training_data' not in st.session_state:
    df = pd.read_csv('training_samples.csv')
    st.session_state.training_data = df.reset_index(drop=True)
    st.session_state.training_index = user_info.get('qnt_class', 0)
    st.session_state.training_done = user_info.get('qnt_class', 0)


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

# Mapeamento para corrigir as chaves do selectbox para os nomes das colunas no DataFrame
# Isso é crucial para que a função 'select' possa buscar o gabarito corretamente
KEY_TO_ROW_MAP = {
    'h_sent': 'sent_manchete',
    'h_pol': 'pol_manchete',
    'sent_1': 'sent1',
    'pol_1': 'pol1',
    'sent_2': 'sent2',
    'pol_2': 'pol2',
    'sent_3': 'sent3',
    'pol_3': 'pol3',
    'g_sent': 'sent_geral',
    'g_pol': 'pol_geral',
    'unknown_terms': 'unknown_terms' # Embora não tenha gabarito para este, mantemos a consistência
}

# Função de reset dos campos
def reset_fields():
    # Remove as chaves específicas do session_state para forçar o reset dos widgets
    for key in KEY_TO_ROW_MAP.keys(): # Iterar sobre as chaves que controlam os widgets
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['show_solution'] = False # Garante que a solução não seja mostrada na próxima notícia

# A função 'select' agora vai exibir o gabarito de forma mais controlada
def select(label, options, key):
    default_value = st.session_state.get(key, 'Não selecionado')
    val = st.selectbox(label, options=options, key=key, index=options.index(default_value))

    # Somente mostra o gabarito se show_solution for True e a chave existir no mapeamento
    if st.session_state.get('show_solution', False) and key in KEY_TO_ROW_MAP:
        correct_answer = row[KEY_TO_ROW_MAP[key]]
        if val == correct_answer:
            st.markdown(f'<span style="color: green;">Correto! Gabarito: **{correct_answer}**</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color: red;">Incorreto. Gabarito: **{correct_answer}**</span>', unsafe_allow_html=True)
    return val

# Resetar campos no início da execução se a flag 'reset_fields_on_load' estiver ativada
if st.session_state.pop('reset_fields_on_load', False):
    reset_fields()

st.subheader(row['manchete'])
show_definitions(row['manchete'])

cols = st.columns(2)
with cols[0]: headline_sent = select('Sentimento da Manchete', EMOTIONS, 'h_sent')
with cols[1]: headline_pol = select('Polaridade da Manchete', POLARITIES, 'h_pol')

st.write('---')

sentiments = []
polarities = []
sentences = [row['f1'], row['f2'], row['f3']]
for i, sent in enumerate(sentences, 1):
    st.text(f'Frase {i}: {sent}')
    show_definitions(sent)
    cols = st.columns(2)
    with cols[0]: sentiments.append(select(f'Sentimento {i}', EMOTIONS, f'sent_{i}'))
    with cols[1]: polarities.append(select(f'Polaridade {i}', POLARITIES, f'pol_{i}'))
    st.write('---')

cols = st.columns(2)
with cols[0]: g_sent = select('Sentimento Geral', EMOTIONS, 'g_sent')
with cols[1]: g_pol = select('Polaridade Geral', POLARITIES, 'g_pol')

unknown_terms = st.text_input(
    'Termos que você não conhece (separe por vírgulas)', key='unknown_terms',
    value=st.session_state.get('unknown_terms', '') # Adiciona valor padrão do session_state
)

# Lógica dos botões
# O botão 'Verificar Resposta' agora apenas define 'show_solution' para True
# e 'reset_fields_on_load' para False (para não resetar os campos ainda)
if not st.session_state.get('show_solution', False): # Só mostra este botão se a solução não estiver sendo exibida
    cols = st.columns(2)
    if cols[0].button('Verificar Resposta', use_container_width=True):
        # Verifica se todos os campos obrigatórios foram preenchidos
        all_filled = all([headline_sent != 'Não selecionado', headline_pol != 'Não selecionado',
                        g_sent != 'Não selecionado', g_pol != 'Não selecionado'] +
                       [s != 'Não selecionado' for s in sentiments] +
                       [p != 'Não selecionado' for p in polarities])

        if all_filled:
            st.session_state['show_solution'] = True
            # Não avança o índice aqui, apenas mostra a solução
            # O índice só avança no botão "Próxima Notícia"
            st.rerun()
        else:
            st.error('Preencha todos os campos antes de verificar.')

    if cols[1].button('Pular Notícia', use_container_width=True):
        if unknown_terms:
            create_terms(row.name, unknown_terms.split(',')) # row.name para o id da notícia no training
        
        # Avança para a próxima notícia
        if st.session_state.training_index < len(data) - 1:
            st.session_state.training_index += 1
        else:
            st.session_state.training_index = 0 # Volta para o início se for a última notícia
        
        st.session_state['reset_fields_on_load'] = True # Ativa o reset para a próxima execução
        st.rerun()

else: # Se 'show_solution' for True, mostra o botão 'Próxima Notícia'
    if st.button('Próxima Notícia', use_container_width=True):
        # Salvar a quantidade de classificações feitas (se desejar contabilizar no treinamento)
        st.session_state.training_done += 1
        update_user_qnt_class(user_id, st.session_state.training_done)
        
        # Avança para a próxima notícia
        if st.session_state.training_index < len(data) - 1:
            st.session_state.training_index += 1
        else:
            st.success('Treinamento finalizado!')
            st.session_state.training_index = 0 # Volta para o início se for a última notícia
        
        st.session_state['reset_fields_on_load'] = True # Ativa o reset para a próxima execução
        st.rerun()