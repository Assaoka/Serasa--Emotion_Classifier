import streamlit as st
import auth_utils

auth_utils.get_or_register_user()

st.title("Treinamento")

st.write("Nesta etapa mostramos exemplos de classificação corretos e um pequeno teste.")

st.subheader("Exemplo 1")
st.markdown("**Manchete:** Banco Central corta juros.\n**Classificação:** Felicidade\n**Justificativa:** A notícia indica melhora econômica.")

st.subheader("Exemplo 2")
st.markdown("**Manchete:** Empresa anuncia demissões em massa.\n**Classificação:** Tristeza\n**Justificativa:** Demissões costumam gerar sentimento negativo.")

st.subheader("Teste Rápido")

with st.form("training_test"):
    option = st.selectbox(
        "Qual o sentimento da manchete 'Inflação atinge recorde do ano'?",
        ["Felicidade", "Tristeza", "Medo"],
    )
    submitted = st.form_submit_button("Responder")
    if submitted:
        if option == "Tristeza":
            st.success("Resposta correta! Você está pronto para classificar.")
        else:
            st.error("Resposta incorreta. Reveja os exemplos e tente novamente.")
