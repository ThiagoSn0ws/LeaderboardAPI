from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_player, hash_password, verify_password
from app.database import get_db
from app.models import Player
from app.schemas import PlayerCreate, PlayerOut, NewPassword

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/register", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def register_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    existing = db.query(Player).filter(Player.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Esse username já está em uso")

    player = Player(username=payload.username, hashed_password=hash_password(payload.password), bio=payload.bio)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.get("/me", response_model=PlayerOut)
def read_current_player(current_player: Player = Depends(get_current_player)):
    return current_player

@router.patch("/players/me")
def change_password(payload: NewPassword, current_player: Player = Depends(get_current_player), db: Session = Depends(get_db)):

    if not(verify_password(payload.current_password, current_player.hashed_password)):
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Senha incorreta.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    else: 
        current_player.hashed_password = hash_password(payload.new_password)
        db.commit()
        return {"detail": "Senha alterada com sucesso."}