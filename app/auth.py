"""
Autenticação: hashing de senha e emissão/validação de token JWT.

Fluxo:
1. Jogador se registra -> senha é transformada em hash (nunca guardamos a
   senha em texto puro).
2. Jogador faz login -> se a senha bater com o hash, geramos um token JWT
   assinado, que expira depois de um tempo.
3. Nas rotas protegidas, o jogador manda esse token no header
   "Authorization: Bearer <token>" e nós o validamos.
"""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Player

# Em produção, defina SECRET_KEY como variável de ambiente -- nunca deixe
# uma chave fixa no código de um projeto real. Aqui há um valor padrão só
# para facilitar rodar o projeto localmente.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-troque-isso-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_player(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Player:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    player = db.query(Player).filter(Player.username == username).first()
    if player is None:
        raise credentials_exception
    return player
