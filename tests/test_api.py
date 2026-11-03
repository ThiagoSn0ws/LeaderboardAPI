"""
Testes automatizados da API.

Usamos um banco SQLite em memória separado do banco "de verdade"
(leaderboard.db), só para os testes -- assim rodar `pytest` nunca mexe
nos seus dados reais. Isso é feito sobrescrevendo a dependency `get_db`
do FastAPI.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool faz todas as conexões de teste reaproveitarem a mesma conexão
# SQLite em memória -- sem isso, cada sessão veria um banco em branco diferente.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    """Recria as tabelas do zero antes de cada teste, pra eles não interferirem entre si."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def register_and_login(username="player1", password="senha123"):
    client.post("/players/register", json={"username": username, "password": password})
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_player():
    response = client.post(
        "/players/register", json={"username": "novato", "password": "senha123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "novato"
    assert "hashed_password" not in body  # nunca deve vazar o hash da senha


def test_register_duplicate_username_fails():
    client.post("/players/register", json={"username": "dup", "password": "senha123"})
    response = client.post(
        "/players/register", json={"username": "dup", "password": "outrasenha"}
    )
    assert response.status_code == 400


def test_login_with_wrong_password_fails():
    client.post("/players/register", json={"username": "user1", "password": "senha123"})
    response = client.post(
        "/auth/login", data={"username": "user1", "password": "senha_errada"}
    )
    assert response.status_code == 401


def test_submit_score_requires_auth():
    response = client.post("/scores", json={"game_name": "xadrez", "points": 100})
    assert response.status_code == 401


def test_submit_score_and_read_it_back():
    headers = register_and_login("jogador2")
    response = client.post(
        "/scores", json={"game_name": "xadrez", "points": 250}, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["points"] == 250

    response = client.get("/players/jogador2/scores")
    assert response.status_code == 200
    scores = response.json()
    assert len(scores) == 1
    assert scores[0]["game_name"] == "xadrez"


def test_leaderboard_orders_by_best_score():
    headers_a = register_and_login("alice")
    headers_b = register_and_login("bob")

    client.post("/scores", json={"game_name": "xadrez", "points": 100}, headers=headers_a)
    client.post("/scores", json={"game_name": "xadrez", "points": 300}, headers=headers_b)
    client.post("/scores", json={"game_name": "xadrez", "points": 150}, headers=headers_a)

    response = client.get("/leaderboard", params={"game_name": "xadrez"})
    assert response.status_code == 200
    entries = response.json()

    assert entries[0]["username"] == "bob"
    assert entries[0]["best_score"] == 300
    assert entries[0]["rank"] == 1
    assert entries[1]["username"] == "alice"
    assert entries[1]["best_score"] == 150  # a melhor pontuação de alice, não a última
