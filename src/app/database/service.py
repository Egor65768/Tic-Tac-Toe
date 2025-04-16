from typing import Optional
from app.database.model import User_Status, Invite_Status
from app.domain.current_game import Current_Game
from app.domain.user import User
from flask_sqlalchemy import SQLAlchemy
from app.database import model
from copy import deepcopy
from app.domain.board import GameBoard, Constant
import uuid
import sqlalchemy as sa
from flask import session


class DB_Service:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def add_in_db_new_game(self, game: Current_Game):
        try:
            cg = model.Current_Game(
                user1_id=game.user1_id,
                user2_id=game.user2_id,
                game_id=game.game_id,
                size=game.game_board.size,
                board=game.game_board.board,
                current_move=game.current_move,
            )
            self.db.session.add(cg)
            self.db.session.flush()
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            print(f"Ошибка при добавлении игры.{e}")

    def get_game(self, game_uuid) -> Optional[Current_Game]:
        try:
            current_game = self.db.session.get(model.Current_Game, str(game_uuid))
            if current_game is None:
                return None
            print(type(current_game.board))
            game = Current_Game(
                current_game.user1_id,
                current_game.user2_id,
                current_game.game_id,
                GameBoard(current_game.size, deepcopy(current_game.board)),
                current_game.current_move,
            )
            return game
        except Exception as e:
            self.db.session.rollback()
            print(f"Ошибка при запросе игры.{e}")

    def save_game(self, game: Current_Game):
        current_game = self.db.session.get(model.Current_Game, str(game.game_id))
        if current_game is not None:
            current_game.board = game.game_board.board
            current_game.current_move = game.current_move
            self.db.session.add(current_game)
            self.db.session.commit()
        else:
            self.add_in_db_new_game(game)

    def get_user(self, user_id: uuid.UUID):
        user_db = self.db.session.scalar(
            sa.select(model.User).where(model.User.user_id == user_id)
        )
        return user_db

    def save_user(self, user: User) -> bool:
        user_db = self.db.session.scalar(
            sa.select(model.User).where(model.User.login == user.login)
        )
        if user_db is not None:
            return False
        try:
            new_user_db = model.User(
                user_id=user.id,
                name=user.name,
                login=user.login,
                status=User_Status.OFFLINE,
            )
            new_user_db.set_password(user.password)
            self.db.session.add(new_user_db)
            self.db.session.commit()
            rating_user = model.Table_Leader(
                user_id=user.id, victory=0, defeats=0, draws=0
            )
            self.db.session.add(rating_user)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            print(f"Ошибка при сохранении юзера.{e}")
            return False

    def set_status(self, status: int, user_login: str = None):
        if user_login is None:
            user = self.get_user_login(session["user_login"])
        else:
            user = self.get_user_login(user_login)
        if user is not None:
            user.status = status
            self.db.session.commit()

    def get_wait_users(self):
        pending_users = self.db.session.scalars(
            sa.select(model.User).where(
                (model.User.status == User_Status.WAIT_GAME)
                & (model.User.login != session["user_login"])
            )
        ).all()
        return pending_users

    def get_user_login(self, login: str):
        user_db = self.db.session.scalar(
            sa.select(model.User).where(model.User.login == login)
        )
        return user_db

    def get_user_from_rating_table(self, user_uuid):
        user_db = self.db.session.scalar(
            sa.select(model.Table_Leader).where(model.Table_Leader.user_id == user_uuid)
        )
        return user_db

    def get_rating_table(self, number_of_positions: int = None):
        if number_of_positions is None:
            users_rating = self.db.session.scalars(
                sa.select(model.Table_Leader).order_by(
                    sa.desc(model.Table_Leader.victory),
                    sa.desc(model.Table_Leader.draws),
                    model.Table_Leader.defeats,
                )
            ).all()
        else:
            users_rating = self.db.session.scalars(
                sa.select(model.Table_Leader)
                .order_by(
                    sa.desc(model.Table_Leader.victory),
                    sa.desc(model.Table_Leader.draws),
                    model.Table_Leader.defeats,
                )
                .limit(number_of_positions)
            ).all()

        return users_rating

    def get_user_uuid(self, login: str):
        user_db = self.db.session.scalar(
            sa.select(model.User).where(model.User.login == login)
        )
        return user_db.user_id if user_db is not None else user_db

    def get_login_by_uuid(self, user_uuid):
        user = self.get_user(user_uuid)
        if user is not None:
            return user.login
        return None

    def send_invite(self, login: str):
        if session["user_login"] is not None and login is not None:
            if self.check_invite(login):
                new_invite = model.Invite(
                    wait_user=session["user_login"],
                    invite_user=login,
                    status=Invite_Status.WAIT,
                )
                self.db.session.add(new_invite)
                self.db.session.commit()

    def check_invite(self, login: str) -> bool:
        invite = self.db.session.scalar(
            sa.select(model.Invite).where(
                (model.Invite.invite_user == login)
                & (model.Invite.wait_user == session["user_login"])
                & (model.Invite.status == Invite_Status.WAIT)
            )
        )
        return invite is None

    def check_invite_status(self):
        invite = self.db.session.scalar(
            sa.select(model.Invite).where(
                model.Invite.wait_user == session["user_login"]
            )
        )
        status = Invite_Status.REJECTED if invite is None else invite.status
        if status == Invite_Status.ACCEPTED:
            self.del_invite()
        return status

    def del_invite(self):
        invite = self.db.session.scalar(
            sa.select(model.Invite).where(
                model.Invite.wait_user == session["user_login"]
            )
        )
        if invite is not None:
            self.db.session.delete(invite)
            self.db.session.commit()

    def processing_invite(self, login: str, invite_status: int):
        if session["user_login"] is not None and login is not None:
            invite = self.db.session.scalar(
                sa.select(model.Invite).where(
                    (model.Invite.wait_user == login)
                    & (model.Invite.invite_user == session["user_login"])
                )
            )
            if invite is not None and invite_status == Invite_Status.REJECTED:
                self.db.session.delete(invite)
                self.db.session.commit()
            elif invite is not None:
                invite.status = invite_status
                self.db.session.commit()

    def del_current_game(self):
        current_games = self.db.session.scalars(
            sa.select(model.Current_Game).where(
                model.Current_Game.user1_id == self.get_user_uuid(session["user_login"])
            )
        ).all()
        if current_games is not None:
            for game in current_games:
                self.add_game_in_history(game)
                self.db.session.delete(game)
            self.db.session.commit()

    def del_current_game_by_uuid(self, game_id):
        current_game = self.db.session.scalar(
            sa.select(model.Current_Game).where((model.Current_Game.game_id == game_id))
        )
        if current_game is not None:
            self.add_game_in_history(current_game)
            self.db.session.delete(current_game)
            self.db.session.commit()

    def add_game_in_history(self, game: model.Current_Game):
        board = list(game.board)
        game_board = GameBoard(game.size, deepcopy(board))
        user_login = session["user_login"]
        result = game_board.check_winner()
        game_was_over = True
        draw = False
        if result == Constant.VOID:
            if game_board.is_full():
                draw = True
            else:
                game_was_over = False
            winner = (
                game.user2_id
                if self.get_login_by_uuid(game.user1_id) == user_login
                else game.user1_id
            )
            loser = game.user2_id if winner == game.user1_id else game.user1_id
        elif result == Constant.CROSS:
            winner = game.user2_id
            loser = game.user1_id
        else:
            winner = game.user1_id
            loser = game.user2_id
        try:
            cg = model.History_games(
                game_id=game.game_id,
                board=game_board.board,
                winner=winner,
                loser=loser,
                timestamp=game.timestamp,
                draw=draw,
                game_was_over=game_was_over,
            )
            self.db.session.add(cg)
            self.leaderboard_update(loser, winner, draw)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            print(f"Ошибка при добавлении игры.{e}")

    def leaderboard_update(self, loser_uuid, winner_uuid, draw: bool):
        loser = (
            self.get_user_from_rating_table(loser_uuid)
            if loser_uuid is not None
            else None
        )
        winner = (
            self.get_user_from_rating_table(winner_uuid)
            if winner_uuid is not None
            else None
        )
        if draw:
            if loser is not None:
                loser.draws += 1
            if winner is not None:
                winner.draws += 1
        else:
            if loser is not None:
                loser.defeats += 1
            if winner is not None:
                winner.victory += 1

    def get_games_user(self, user_uuid):
        return self.db.session.scalars(
            sa.select(model.History_games).where(
                sa.or_(
                    model.History_games.winner == user_uuid,
                    model.History_games.loser == user_uuid,
                )
            )
        ).all()

    def get_all_games(self):
        return self.db.session.scalars(
            sa.select(model.History_games).order_by(model.History_games.timestamp)
        ).all()

    def users_wait(self):
        wait_users = list()
        pending_user = self.db.session.scalars(
            sa.select(model.Invite).where(
                (model.Invite.invite_user == session["user_login"])
            )
        )
        if pending_user is not None:
            for user in pending_user:
                wait_users.append(self.get_user_login(user.wait_user))
        return wait_users

    def get_user_game(self):
        current_game = self.db.session.scalar(
            sa.select(model.Current_Game).where(
                sa.or_(
                    model.Current_Game.user1_id
                    == self.get_user_uuid(session["user_login"]),
                    model.Current_Game.user2_id
                    == self.get_user_uuid(session["user_login"]),
                )
            )
        )
        return current_game
