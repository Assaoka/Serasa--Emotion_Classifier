import streamlit as st
import auth_utils

user_id = auth_utils.get_or_register_user()
auth_utils.sidebar_login_info(show=True)

st.markdown("""
# Anotação de Sentimentos em Notícias Financeiras

Bem-vindo ao nosso site, desenvolvido para envolver alunos no processo de anotação e análise de notícias econômicas em português. Aqui, você ajudará a construir uma base de dados de sentimentos e emoções aplicados a textos jornalísticos.

---

## 📝 Funcionalidades Principais

1. **Classificação de Sentimentos e Emoções**  
   - **Polaridade**: Positivo, Neutro ou Negativo  
   - **Emoções de Ekman**: Alegria, Tristeza, Medo, Raiva, Surpresa, Nojo ou Desprezo  

2. **Treinamento Guiado**  
   - 3 notícias divididas em:  
     - Título  
     - Frase 1 (início)  
     - Frase 2 (meio)  
     - Frase 3 (fim)  
   - Duplo seletor para cada trecho: polaridade + emoção  
   - Avaliação geral ao final de cada notícia  

3. **Minhas Avaliações**  
   - Consulte todas as suas classificações  
   - Baixe os dados em CSV para estudo ou consulta  

---

## 🔐 Acesso e Autenticação

1. **Login Inicial**  
   - Clique em **“Login via Google”**  
   - Autentique-se com sua conta Google  
   - Responda a perguntas rápidas para definirmos seu perfil  

2. **Visitas Futuras**  
   - Acesso automático sem necessidade de novo login  
   - Permissão liberada para todas as abas, exceto a de classificação principal (até concluir o treinamento)  

---

## 🎯 Fluxo de Uso

1. **Treinamento Inicial**  
   - Classifique 3 notícias-treinamento  
   - Aprenda os critérios de polaridade e emoção  
   - Familiarize-se com interface e botões (Salvar / Pular)  

2. **Classificação Principal**  
   - Mesma lógica do treinamento  
   - Suas anotações passam a integrar a base oficial  

3. **Acompanhamento**  
   - Acesse **“Minhas Avaliações”** para ver seu histórico  
   - Exporte resultados sempre que desejar  

---

## 💬 Feedback e Suporte

Se encontrar erros, inconsistências ou tiver sugestões de melhoria, entre em contato:

- **João Assaoka**: joao.assaoka@unifesp.br  
- **Thomas Correia**: correia.thomas@unifesp.br  

Agradecemos sua colaboração e empenho no projeto!  
""")
