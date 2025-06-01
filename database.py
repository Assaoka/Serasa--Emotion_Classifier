import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import streamlit as st

# Variáveis globais que serão inicializadas pela função init
engine = None
SessionLocal = None
Base = declarative_base()

# Definição dos modelos
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    idade = Column(Integer, nullable=True)         
    genero = Column(String, nullable=True)        # gênero como string (ex: 'Masculino', 'Feminino', 'Outro')
    escolaridade = Column(String, nullable=True)  # nível de escolaridade como string (ex: 'Ensino Médio', 'Superior')
    
    evaluations = relationship("Evaluation", back_populates="user")

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String, nullable=False)
    link = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    evaluations = relationship("Evaluation", back_populates="news")

class Evaluation(Base):
    __tablename__ = 'evaluations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    # Classificações para manchete (inteiros: 1-7 emoção, 1-3 polaridade)
    headline_sentiment = Column(Integer, nullable=False)
    headline_polarity = Column(Integer, nullable=False)
    # Classificações para as 3 frases do resumo
    sentence1_sentiment = Column(Integer, nullable=False)
    sentence1_polarity = Column(Integer, nullable=False)
    sentence2_sentiment = Column(Integer, nullable=False)
    sentence2_polarity = Column(Integer, nullable=False)
    sentence3_sentiment = Column(Integer, nullable=False)
    sentence3_polarity = Column(Integer, nullable=False)
    # Classificação geral
    general_sentiment = Column(Integer, nullable=False)
    general_polarity = Column(Integer, nullable=False)

    user = relationship("User", back_populates="evaluations")
    news = relationship("News", back_populates="evaluations")


def init(db_url: str):
    """Inicializa a conexão com o banco de dados e cria as tabelas."""
    global engine, SessionLocal
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

def create_user(email: str, idade: int, genero: str, escolaridade: str) -> int:
    session = SessionLocal()
    try:
        user = User(email=email, idade=idade, genero=genero, escolaridade=escolaridade)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id
    except IntegrityError:
        session.rollback()
        existing = session.query(User).filter_by(email=email).first()
        return existing.id
    finally:
        session.close()



def create_news(headline: str, link: str, summary: str) -> int:
    """Insere uma notícia e retorna o ID."""
    session = SessionLocal()
    try:
        news = News(headline=headline, link=link, summary=summary)
        session.add(news)
        session.commit()
        session.refresh(news)
        return news.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def create_evaluation(user_id: int, news_id: int,
                       headline_sentiment: int, headline_polarity: int,
                       sentence_sentiments: list, sentence_polarities: list,
                       general_sentiment: int, general_polarity: int) -> None:
    """Insere uma avaliação no banco."""
    session = SessionLocal()
    try:
        eval_obj = Evaluation(
            user_id=user_id,
            news_id=news_id,
            headline_sentiment=headline_sentiment,
            headline_polarity=headline_polarity,
            sentence1_sentiment=sentence_sentiments[0],
            sentence1_polarity=sentence_polarities[0],
            sentence2_sentiment=sentence_sentiments[1],
            sentence2_polarity=sentence_polarities[1],
            sentence3_sentiment=sentence_sentiments[2],
            sentence3_polarity=sentence_polarities[2],
            general_sentiment=general_sentiment,
            general_polarity=general_polarity,
            date=datetime.utcnow()
        )
        session.add(eval_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_random_news_with_three_sentences():
    """Retorna uma notícia cujo resumo contém exatamente 3 frases."""
    session = SessionLocal()
    try:
        all_news = session.query(News).all()
        # Filtra apenas resumos com exatamente 3 frases (separadas por ". ")
        filtered = [n for n in all_news if len(n.summary.split('. ')) == 3]
        if not filtered:
            return None
        return random.choice(filtered)
    finally:
        session.close()

def email_exists(email: str) -> bool:
    """Verifica se o e-mail já está cadastrado na base."""
    session = SessionLocal()
    try:
        exists = session.query(User).filter_by(email=email).first() is not None
        return exists
    finally:
        session.close()

def register_user_with_questions(email: str):
    """Verifica se o e-mail existe e, se não existir, cadastra o usuário com perguntas adicionais."""
    if email_exists(email):
        st.success("Usuário já cadastrado.")
        return
    else:
        st.header("Novo Usuário - Responda algumas perguntas:")
        age = st.number_input("Quantos anos você tem?", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Qual o seu gênero?", ["Masculino", "Feminino", "Outro"])
        education = st.selectbox("Qual o seu nível de escolaridade?", [
            "Ensino Fundamental", 
            "Ensino Médio", 
            "Superior", 
            "Pós-graduação", 
            "Mestrado", 
            "Doutorado",
            "Outro"
        ])

        if st.button("Confirmar Cadastro"):
            user_id = create_user(email, age, gender, education)  # passando os novos dados
            st.success(f"Usuário criado com ID {user_id}!")
            st.write(f"Idade: {age}")
            st.write(f"Gênero: {gender}")
            st.write(f"Escolaridade: {education}")
