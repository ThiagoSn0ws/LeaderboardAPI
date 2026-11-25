"""Modelos SQLAlchemy: como as tabelas do banco de dados são estruturadas."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    scores: Mapped[list["Score"]] = relationship(
        "Score", back_populates="player", cascade="all, delete-orphan"
    )
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)




class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    game_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    player: Mapped["Player"] = relationship("Player", back_populates="scores")
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=True)

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    season_name: Mapped[str] = mapped_column(String(100),index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
