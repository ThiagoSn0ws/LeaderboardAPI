"""
Configuração da conexão com o banco de dados.

Usamos SQLite aqui porque é um arquivo só (leaderboard.db) e não exige
instalar nada extra -- perfeito para desenvolver localmente e para o
avaliador do seu currículo rodar o projeto sem fricção. Trocar para
Postgres no futuro é só mudar a DATABASE_URL abaixo.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./leaderboard.db")

# check_same_thread só é necessário para SQLite (não existe em Postgres/MySQL)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão de banco por requisição e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
