from app.database.model import History_games, Table_Leader
from app.domain.history_game import History_Game, Constant, All_History_Game
from app.domain.rating_user import Rating_User
from app.web.route import db_service
from typing import List


class Domain_mapper:
    @staticmethod
    def from_dbmodel_to_domain_history_game(
        game: History_games, user_uuid
    ) -> History_Game:
        opponent_uuid = game.winner if game.loser == user_uuid else game.loser
        if not game.draw:
            result = Constant.WIN if game.winner == user_uuid else Constant.LOSE
        else:
            result = Constant.DRAW
        opponent = db_service.get_login_by_uuid(opponent_uuid)
        return History_Game(
            timestamp=game.timestamp,
            game_was_over=game.game_was_over,
            opponent=opponent,
            result=result,
            board=list(game.board),
        )

    @staticmethod
    def from_dbmodel_to_domain_all_history_game(
        game: History_games,
    ) -> All_History_Game:
        game_status = Constant.DRAW if game.draw else Constant.WIN
        user1 = db_service.get_login_by_uuid(game.winner)
        user2 = db_service.get_login_by_uuid(game.loser)
        if user1 is None:
            user1 = "Бот"
        if user2 is None:
            user2 = "Бот"
        return All_History_Game(
            timestamp=game.timestamp,
            game_was_over=game.game_was_over,
            user1=user1,
            user2=user2,
            result=game_status,
        )

    @staticmethod
    def from_list_dbmodel_to_list_domain_history_game(
        games: List[History_games], user_uuid=None
    ) -> List[History_Game | All_History_Game]:
        domain_games = list()
        for game in games:
            if user_uuid is not None:
                domain_games.insert(
                    0,
                    Domain_mapper.from_dbmodel_to_domain_history_game(game, user_uuid),
                )
            else:
                domain_games.insert(
                    0, Domain_mapper.from_dbmodel_to_domain_all_history_game(game)
                )
        return domain_games

    @staticmethod
    def from_dbmodel_to_domain_rating_user(
        user: Table_Leader, position: int
    ) -> Rating_User:
        user_login = db_service.get_login_by_uuid(user.user_id)
        return Rating_User(
            rating=position,
            user_uuid=user.user_id,
            user_login=user_login,
            win=user.victory,
            draw=user.draws,
            lose=user.defeats,
        )

    @staticmethod
    def from_list_dbmodel_to_list_domain_user_rating(
        users: List[Table_Leader],
    ) -> List[Rating_User]:
        domain_rating = list()
        position = 1
        for user in users:
            domain_rating.append(
                Domain_mapper.from_dbmodel_to_domain_rating_user(user, position)
            )
            position += 1
        return domain_rating
