from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password
from app.database import get_db
from app.models import Player
from app.schemas import Token
from datetime import timedelta
from datetime import datetime


router = APIRouter(prefix="/auth", tags=["auth"])

tentativas = {}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dados_tentativas = tentativas.get(form_data.username, {"numero": 0, "horario": None})

    if dados_tentativas["numero"] >= 5:
        if datetime.utcnow() - dados_tentativas["horario"] < timedelta(minutes=5):
            raise HTTPException(status_code=429, detail="Você está com restrição de tempo. Aguarde e volte mais tarde.")
        else:
            dados_tentativas = {"numero": 0, "horario": None}

    player = db.query(Player).filter(Player.username == form_data.username).first()
    if not player or not verify_password(form_data.password, player.hashed_password):
        tentativas[form_data.username] = {"numero": dados_tentativas["numero"] + 1, "horario": datetime.utcnow()}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        tentativas[form_data.username] = {"numero": 0, "horario": None}

    access_token = create_access_token(data={"sub": player.username})
    return Token(access_token=access_token)