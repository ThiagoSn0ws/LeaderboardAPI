"""
Schemas Pydantic: definem o "formato" dos dados que entram e saem da API.

É a diferença entre o modelo do banco (models.py, o que é salvo) e o que
de fato é aceito/exposto pela API -- por exemplo, nunca devolvemos a senha
com hash de um jogador numa resposta.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    bio: str | None = Field(default=None, max_length=255)
#PlayerCreate recebe os dados que são usados para salvar um Player no banco

class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    bio: str | None = None
#PlayerOut so devolve os campos    


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ScoreCreate(BaseModel):
    game_name: str = Field(min_length=1, max_length=100)
    points: int = Field(ge=0, le=1000000)


class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_name: str
    points: int
    created_at: datetime


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    game_name: str
    best_score: int

class NewPassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=100)
