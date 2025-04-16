import sqlalchemy.orm as so
from sqlalchemy import String, Integer, JSON, ForeignKey, UUID, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db
import uuid
from typing import Optional


class User_Status:
    WAIT_GAME = 0
    IN_GAME = 1
    ONLINE = 2
    OFFLINE = 3


class Invite_Status:
    WAIT = 0
    ACCEPTED = 1
    REJECTED = 2


class User(db.Model):
    user_id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    name: so.Mapped[str] = so.mapped_column(String(30))
    login: so.Mapped[str] = so.mapped_column(String(50), unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(String(256))
    status: so.Mapped[int] = so.mapped_column(Integer)

    def get_id(self):
        return self.user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Current_Game(db.Model):
    game_id: so.Mapped[uuid.UUID] = so.mapped_column(String, primary_key=True)
    size: so.Mapped[int] = so.mapped_column(Integer)
    board: so.Mapped[dict] = so.mapped_column(JSON)
    user1_id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), ForeignKey(User.user_id), index=True
    )
    user2_id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), ForeignKey(User.user_id), index=True, nullable=True
    )
    current_move: so.Mapped[uuid.UUID]
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )


class History_games(db.Model):
    game_id: so.Mapped[uuid.UUID] = so.mapped_column(String, primary_key=True)
    board: so.Mapped[dict] = so.mapped_column(JSON)
    winner: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), ForeignKey(User.user_id), index=True, nullable=True
    )
    loser: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), ForeignKey(User.user_id), index=True, nullable=True
    )
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )
    draw: so.Mapped[bool] = so.mapped_column(Boolean)
    game_was_over: so.Mapped[bool] = so.mapped_column(Boolean)


class Invite(db.Model):
    id_invite: so.Mapped[int] = so.mapped_column(Integer, primary_key=True)
    wait_user: so.Mapped[str] = so.mapped_column(
        String, ForeignKey(User.login), index=True
    )
    invite_user: so.Mapped[str] = so.mapped_column(
        String, ForeignKey(User.login), index=True
    )
    status: so.Mapped[int] = so.mapped_column(Integer)


class Table_Leader(db.Model):
    user_id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), ForeignKey(User.user_id), primary_key=True, index=True
    )
    victory: so.Mapped[int] = so.mapped_column(Integer)
    defeats: so.Mapped[int] = so.mapped_column(Integer)
    draws: so.Mapped[int] = so.mapped_column(Integer)
