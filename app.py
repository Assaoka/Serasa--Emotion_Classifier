import streamlit as st
# Importe suas funções de banco de dados.
# Certifique-se de que 'database.py' não contém mais a lógica de UI para 'register_user_with_questions'.
from database import init, create_user, create_evaluation, get_random_news_with_three_sentences, get_user_by_email

# --- Inicialização e Constantes ---
# O segredo do Postgres ainda é necessário para o banco de dados
DATABASE_URL = st.secrets["auth"]["postgres"]
init(DATABASE_URL)

# ATENÇÃO: Adicionado 'Não selecionado' como primeira opção
EMOTIONS = ['Não selecionado', 'Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo']
POLARITIES = ['Não selecionado', 'Positivo', 'Neutro', 'Negativo']

# --- Funções Auxiliares ---
def show_classification_controls(label: str, key_prefix: str):
    st.subheader(label)
    col1, col2 = st.columns(2)
    with col1:
        selected_sent = st.selectbox("Sentimento", options=EMOTIONS, key=f"sent_{key_prefix}")
        # Retorna o índice da opção selecionada. 'Não selecionado' será 0.
        sent_value = EMOTIONS.index(selected_sent)
    with col2:
        selected_pol = st.selectbox("Polaridade", options=POLARITIES, key=f"pol_{key_prefix}")
        # Retorna o índice da opção selecionada. 'Não selecionado' será 0.
        pol_value = POLARITIES.index(selected_pol)
    return sent_value, pol_value

# Nova função de validação
def validate_selections(evals, sentence_sentiments, sentence_polarities):
    """Verifica se todos os campos de classificação foram preenchidos (não são 0)."""
    # Valida manchete
    if evals['headline_sentiment'] == 0 or evals['headline_polarity'] == 0:
        return False
    # Valida classificação geral
    if evals['general_sentiment'] == 0 or evals['general_polarity'] == 0:
        return False
    # Valida as frases
    for i in range(3): # Assumindo sempre 3 frases
        if sentence_sentiments[i] == 0 or sentence_polarities[i] == 0:
            return False
    return True


st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 3em;
    font-size: 1em;
}
</style>
""", unsafe_allow_html=True)

# --- Nova função para o formulário de cadastro de novo usuário ---
def display_registration_form(email: str):
    """
    Exibe o formulário de cadastro para novos usuários.
    Retorna True se o cadastro for concluído com sucesso, False caso contrário.
    """
    st.header("Bem-vindo(a) ao nosso aplicativo!")
    st.subheader("Para começar, por favor, complete seu cadastro:")

    with st.form("user_registration_form"):
        age = st.number_input("Quantos anos você tem?", min_value=1, max_value=120, step=1, key="reg_age")
        gender = st.selectbox("Qual o seu gênero?", ["Masculino", "Feminino", "Outro"], key="reg_gender")
        education = st.selectbox("Qual o seu nível de escolaridade?", [
            "Ensino Fundamental",
            "Ensino Médio",
            "Superior",
            "Pós-graduação",
            "Mestrado",
            "Doutorado",
            "Outro"
        ], key="reg_education")

        submitted = st.form_submit_button("Confirmar Cadastro")

        if submitted:
            try:
                user_id = create_user(email, age, gender, education)
                st.success(f"Cadastro concluído! Bem-vindo(a)!")
                # Armazena o user_id na sessão para uso imediato
                st.session_state['user_id'] = user_id
                return True # Indica que o cadastro foi bem-sucedido
            except Exception as e:
                st.error(f"Erro ao cadastrar usuário: {e}")
                return False
    return False # Formulário não submetido ou não concluído ainda

# --- Lógica Principal da Aplicação ---

# 1. Verifica se o usuário está autenticado
if not st.experimental_user.is_logged_in:
    st.info("Você não está autenticado.")
    with st.sidebar:
        st.header("Login")
        if st.button("Entrar com Google"):
            st.login("auth0")
    st.stop() # Para a execução do script se o usuário não estiver logado

# 2. Usuário está logado, obtém informações do usuário
userinfo = st.experimental_user
user_email = userinfo.email

if not user_email:
    st.error("Não foi possível obter o email do usuário. Por favor, tente novamente.")
    st.logout() # Força o logout se o email não estiver disponível
    st.rerun()

# Inicializa o estado da sessão para o fluxo de novo usuário, se ainda não estiver definido
if 'is_new_user_flow' not in st.session_state:
    st.session_state['is_new_user_flow'] = False # Por padrão, não é um novo usuário

# 3. Verifica se o usuário existe no banco de dados
user_from_db = get_user_by_email(user_email)

# 4. Lógica Condicional baseada na existência do usuário
if user_from_db is None: # É um novo usuário (primeiro acesso)
    st.session_state['is_new_user_flow'] = True # Ativa o fluxo de novo usuário

    # Exibe o formulário de cadastro
    registration_completed = display_registration_form(user_email)

    if registration_completed:
        # Se o cadastro foi bem-sucedido, transiciona para a aplicação principal
        st.session_state['is_new_user_flow'] = False
        st.rerun() # Recarrega a página para exibir o conteúdo principal
    else:
        st.stop() # Mantém o formulário de cadastro na tela até ser concluído

else: # É um usuário existente
    st.session_state['is_new_user_flow'] = False # Garante que o fluxo de novo usuário está desativado

    # Define o user_id a partir do banco de dados para o usuário existente
    user_id = user_from_db["id"]
    st.session_state['user_id'] = user_id

    # Exibe informações do usuário logado na barra lateral
    with st.sidebar:
        st.header("Usuário Autenticado")
        st.write(f"👤 {userinfo.name or 'Nome não disponível'}")
        st.write(f"✉️ {userinfo.email or 'Email não disponível'}")
        if st.button("Sair"):
            st.logout()
            st.rerun()

    # --- Lógica Principal de Avaliação de Notícias (para usuários existentes) ---
    # Carrega notícia da sessão ou captura nova
    if 'news_id' not in st.session_state:
        news_item = get_random_news_with_three_sentences()
        if not news_item:
            st.error("Não há notícias com resumo contendo exatamente 3 frases.")
            st.stop()
        st.session_state['news_id'] = news_item.id
        st.session_state['news_headline'] = news_item.headline
        st.session_state['news_summary'] = news_item.summary

    # Recupera detalhes da notícia atual
    current_news_id = st.session_state['news_id']
    current_headline = st.session_state['news_headline']
    current_summary = st.session_state['news_summary']

    # Exibe a manchete
    st.header(current_headline)

    # Divide o resumo em 3 frases
    sentences = current_summary.split('. ')
    sentences = [s if s.endswith('.') else s + '.' for s in sentences]

    # Coleta as classificações
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

    # Função para limpar os selectboxes
    def clear_classification_selections():
        # Limpa as chaves dos selectboxes no session_state
        for key_prefix in ["headline", "general"]:
            if f"sent_{key_prefix}" in st.session_state:
                del st.session_state[f"sent_{key_prefix}"]
            if f"pol_{key_prefix}" in st.session_state:
                del st.session_state[f"pol_{key_prefix}"]
        for i in range(1, 4): # Para as 3 frases
            if f"sent_sent_{i}" in st.session_state:
                del st.session_state[f"sent_sent_{i}"]
            if f"pol_sent_{i}" in st.session_state:
                del st.session_state[f"pol_sent_{i}"]


    # Botão para salvar avaliação
    def save_and_next():
        create_evaluation(
            user_id=user_id, # Usa o user_id obtido do DB ou do novo cadastro
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
        clear_classification_selections() # Limpa os selectboxes
        st.rerun()

    # Função para pular a notícia
    def skip_news():
        next_news = get_random_news_with_three_sentences()
        if next_news:
            st.session_state['news_id'] = next_news.id
            st.session_state['news_headline'] = next_news.headline
            st.session_state['news_summary'] = next_news.summary
        clear_classification_selections() # Limpa os selectboxes
        st.rerun()

    # Adiciona os botões de ação em colunas para melhor layout
    col_save, col_skip = st.columns(2)
    with col_save:
        if st.button("Salvar Avaliação"):
            # Validação antes de salvar
            if validate_selections(evals, sentence_sentiments, sentence_polarities):
                save_and_next()
            else:
                st.error("Por favor, classifique todos os campos antes de salvar.")
    with col_skip:
        if st.button("Pular Notícia"):
            skip_news()
