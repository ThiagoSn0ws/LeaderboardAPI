from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Player, Score
from app.schemas import LeaderboardEntry

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    game_name: str | None = Query(default=None, description="Filtra o ranking por jogo"),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Ranking com a MELHOR pontuação de cada jogador, do maior para o menor.
    Se `game_name` for passado, filtra só as pontuações daquele jogo.
    """
    query = (
        db.query(
            Player.username,
            Score.game_name,
            func.max(Score.points).label("best_score"),
        )
        .join(Score, Score.player_id == Player.id)
        .group_by(Player.username, Score.game_name)
    )

    if game_name:
        query = query.filter(Score.game_name == game_name)

    results = query.order_by(func.max(Score.points).desc()).limit(limit).all()

    return [
        LeaderboardEntry(rank=i + 1, username=row[0], game_name=row[1], best_score=row[2])
        for i, row in enumerate(results)
    ]

@router.get("/games", response_model=list[str])
def get_games(db: Session = Depends(get_db)):
    """
    Retorna a lista de jogos que possuem pontuações registradas.
    """
    games = db.query(Score.game_name).distinct().all()
    return [game[0] for game in games]