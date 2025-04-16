from app.domain.board import GameBoard
from app.domain.current_game import Constant


class Web_Game_Board:
    def __init__(self, board: GameBoard = None):
        if board is None:
            self.size = Constant.SIZE
            self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        else:
            self.size = board.size
            self.board = board.board


class WebCurrentGame:
    def __init__(
        self, game_uuid, board: GameBoard, user1_id, user2_id=None, current_move=None
    ):
        self.game_uuid = game_uuid
        self.board = Web_Game_Board(board)
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.current_move = current_move if current_move is not None else user1_id
