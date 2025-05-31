import streamlit as st
import pandas as pd
from random import randint
import json
from typing import Tuple, List

# Configuração inicial do Streamlit
st.set_page_config("Emotion Classifier", layout="wide")

# Carregando o dataset
df = pd.read_csv("resumos.csv")

def selecionar_noticia(df: pd.DataFrame) -> pd.Series:
    """Seleciona uma notícia aleatória com exatamente 3 frases no resumo.

    Args:
        df (pd.DataFrame): DataFrame contendo as notícias.

    Returns:
        pd.Series: Linha do DataFrame correspondente à notícia selecionada.
    """
    while True:
        index = randint(0, len(df) - 1)
        linha = df.iloc[index]
        resumo = linha['Resumo'].split('. ')
        if len(resumo) == 3:
            st.session_state['index'] = index
            return linha

def exibir_classes(text: str, header: bool = False) -> Tuple[str, str]:
    """Exibe os controles para classificação de sentimento e polaridade.

    Args:
        text (str): Texto a ser classificado.
        header (bool): Indica se o texto deve ser exibido como cabeçalho.

    Returns:
        Tuple[str, str]: Sentimento e polaridade selecionados.
    """
    sentimentos = ['Felicidade', 'Tristeza', 'Nojo', 'Raiva', 'Medo', 'Surpresa', 'Desprezo']
    polaridades = ['Positivo', 'Neutro', 'Negativo']

    st.write("---")
    if header:
        st.header(text)
    else:
        st.write(text)

    sentimento = st.radio(
        "Selecione o sentimento",
        options=sentimentos,
        key=f"sentimento_{text}",
        horizontal=True
    )

    polaridade = st.radio(
        "Selecione a polaridade",
        options=polaridades,
        key=f"polaridade_{text}",
        horizontal=True
    )
    
    return sentimento, polaridade

def salvar_classificacao(manchete: str, resumo: List[str], classificacoes: List[Tuple[str, str]]) -> None:
    """Salva a classificação em um arquivo JSON.

    Args:
        manchete (str): Manchete da notícia.
        resumo (List[str]): Lista de frases do resumo.
        classificacoes (List[Tuple[str, str]]): Classificações de sentimento e polaridade.
    """
    data = {
        "manchete": {
            "texto": manchete,
            "classificacao": {
                "sentimento": classificacoes[0][0],
                "polaridade": classificacoes[0][1]
            }
        },
        "resumo": [
            {
                "texto": resumo[i],
                "classificacao": {
                    "sentimento": classificacoes[i + 1][0],
                    "polaridade": classificacoes[i + 1][1]
                }
            }
            for i in range(len(resumo))
        ]
    }

    with open("classificacoes.json", "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

# Seleciona uma notícia válida
if st.button("Próximo Aviso") or 'index' not in st.session_state:
    linha = selecionar_noticia(df)
else:
    linha = df.iloc[st.session_state['index']]

manchete = linha['Manchete']
resumo = linha['Resumo'].split('. ')

# Exibe a interface e coleta as classificações
classificacoes = []
classificacoes.append(exibir_classes(manchete, header=True))
for i, frase in enumerate(resumo):
    if i > 0:
        st.write("---")
    classificacoes.append(exibir_classes(frase, header=False))

# Botão para salvar a classificação
if st.button("Salvar Classificação"):
    salvar_classificacao(manchete, resumo, classificacoes)
    st.success("Classificação salva com sucesso!")