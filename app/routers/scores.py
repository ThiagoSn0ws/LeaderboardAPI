from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.auth import get_current_player
from app.database import get_db
from app.models import Player, Score
from app.schemas import ScoreCreate, ScoreOut

router = APIRouter(tags=["scores"])


@router.post("/scores", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
def submit_score(
    payload: ScoreCreate,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """Registra uma pontuação para o jogador autenticado (via token JWT)."""
    score = Score(
        player_id=current_player.id,
        game_name=payload.game_name,
        points=payload.points,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.get("/players/{username}/scores", response_model=list[ScoreOut])
def list_player_scores(username: str, db: Session = Depends(get_db), page: int = Query(default=1, ge=1), page_size: int = Query(default=10, ge=1, le=100)):
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    scores = (
        db.query(Score)
        .filter(Score.player_id == player.id)
        .order_by(Score.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
        
    )
    return scores

@router.delete("/scores/{score_id}")
def delete_score(
    score_id: int,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score não encontrado")

    if score.player_id != current_player.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para apagar essa pontuação")

    db.delete(score)
    db.commit()
    return {"detail": "Pontuação apagada com sucesso"}