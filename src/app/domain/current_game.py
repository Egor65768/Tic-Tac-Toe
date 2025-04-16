import uuid
from app.domain.board import GameBoard, Constant


class Move:
    def __init__(self, x: int, y: int, element: Constant):
        self.x = x
        self.y = y
        self.element = element


class Current_Game:
    def __init__(
        self,
        user1_id,
        user2_id=None,
        game_id=None,
        game_board: GameBoard = None,
        current_move=None,
    ):
        self.game_id = uuid.uuid4() if game_id is None else game_id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.current_move = current_move if current_move is not None else user1_id
        self.game_board = GameBoard() if game_board is None else game_board

    def make_move(self):
        self.current_move = (
            self.user1_id if self.current_move == self.user2_id else self.user2_id
        )

    def cross_or_toe(self, user_id):
        if user_id == self.user1_id:
            return Constant.ZERO
        elif user_id == self.user2_id:
            return Constant.CROSS

    def bot_game(self, x, y):
        from app.domain.game_service import Game_Service, Game_Status

        if self.game_board.set_cell(x, y, Constant.ZERO):
            Game_Service().best_move_bot(self)
            game_status = Game_Service().evaluate_game_status(self.game_board)
        else:
            game_status = Game_Status.FAIL_MOVE
        return game_status

    def online_game(self, x, y, user_uuid):
        from app.domain.game_service import Game_Service, Game_Status

        if self.game_board.set_cell(x, y, self.cross_or_toe(user_uuid)):
            self.make_move()
            game_status = Game_Service().evaluate_game_status(self.game_board)
        else:
            game_status = Game_Status.FAIL_MOVE
        return game_status
