"""Ponto de entrada da aplicação: cria o app FastAPI e registra as rotas."""
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth_router, leaderboard, players, scores

# Cria as tabelas no banco (se ainda não existirem) quando a aplicação sobe.
# Em um projeto maior, isso seria feito com uma ferramenta de migração como o Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Game Leaderboard API",
    description="API de ranking de jogadores para jogos, com autenticação JWT.",
    version="1.0.0",
)

app.include_router(players.router)
app.include_router(auth_router.router)
app.include_router(scores.router)
app.include_router(leaderboard.router)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Game Leaderboard API está no ar",
        "docs": "/docs",
    }
