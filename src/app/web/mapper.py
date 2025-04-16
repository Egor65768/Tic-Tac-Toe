from app.domain.current_game import Current_Game
import model
from app.web.model import WebCurrentGame


class Web_mapper:

    @staticmethod
    def to_web(current_game: Current_Game) -> model.WebCurrentGame:
        web_model = WebCurrentGame(current_game.game_id, current_game.game_board)
        return web_model

    @staticmethod
    def to_domain(web_current_game: WebCurrentGame) -> Current_Game:
        domain_model = Current_Game(web_current_game.game_uuid)
        domain_model.game_board.board = web_current_game.board.board
        domain_model.game_board.size = web_current_game.board.size
        return domain_model
