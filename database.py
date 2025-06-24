import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, func, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, joinedload
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
    le_noticias = Column(Boolean, nullable=True)  # se costuma ler notícias financeiras
    investe = Column(Boolean, nullable=True)      # se costuma investir
    
    evaluations = relationship("Evaluation", back_populates="user")

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String, nullable=False)
    link = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    f1 = Column(String, nullable=False)
    f2 = Column(String, nullable=False)
    f3 = Column(String, nullable=False)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    duration = Column(Float)
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

def create_user(email: str, idade: int, genero: str, escolaridade: str,
                le_noticias: bool, investe: bool) -> int:
    session = SessionLocal()
    try:
        user = User(
            email=email,
            idade=idade,
            genero=genero,
            escolaridade=escolaridade,
            le_noticias=le_noticias,
            investe=investe,
        )
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


def create_news(headline: str, link: str, summary: str, f1: str, f2: str, f3: str,
                prompt_tokens: int = None, completion_tokens: int = None,
                total_tokens: int = None, duration: float = None) -> int:
    """Insere uma notícia e retorna o ID."""
    session = SessionLocal()
    try:
        news = News(
            headline=headline,
            link=link,
            summary=summary,
            f1=f1,
            f2=f2,
            f3=f3,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration=duration,
        )
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
        filtered = [n for n in all_news if n.f1 and n.f2 and n.f3]
        if not filtered:
            return None
        return random.choice(filtered)
    finally:
        session.close()


def get_news_least_classified(user_id: int):
    """Retorna aleatoriamente uma notícia com menor número de avaliações."""
    session = SessionLocal()
    try:
        # total de avaliacoes por noticia (usuarios distintos)
        counts = (
            session.query(
                News,
                func.count(func.distinct(Evaluation.user_id)).label("cnt"),
            )
            .outerjoin(Evaluation)
            .group_by(News.id)
            .all()
        )
        # noticias ja avaliadas pelo usuario
        evaluated = {
            n_id for (n_id,) in session.query(Evaluation.news_id).filter_by(user_id=user_id).all()
        }
        candidates = [
            (news, cnt)
            for news, cnt in counts
            if news.id not in evaluated and news.f1 and news.f2 and news.f3
        ]
        if not candidates:
            return None
        min_cnt = min(cnt for _, cnt in candidates)
        pool = [news for news, cnt in candidates if cnt == min_cnt]
        return random.choice(pool)
    finally:
        session.close()

def get_user_by_email(email: str) -> dict:
    """Busca e retorna um dicionário com as informações do usuário dado o e-mail."""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            return None
        # Retorna as informações do usuário como dicionário
        return {
            "id": user.id,
            "email": user.email,
            "idade": user.idade,
            "genero": user.genero,
            "escolaridade": user.escolaridade,
            "le_noticias": user.le_noticias,
            "investe": user.investe,
        }
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


def get_evaluations_by_user(user_id: int):
    """Retorna todas as avaliações feitas por um usuário, incluindo a notícia."""
    session = SessionLocal()
    try:
        return (
            session.query(Evaluation)
            .options(joinedload(Evaluation.news))
            .filter(Evaluation.user_id == user_id)
            .all()
        )
    finally:
        session.close()

