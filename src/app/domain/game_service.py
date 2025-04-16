from enum import Enum

from app.domain.current_game import Current_Game, Move
from app.domain.board import Constant, GameBoard
from random import randint


class Game_Status(Enum):
    IN_GAME = 0
    WIN_CROSS = 1
    WIN_ZERO = 2
    DRAW = 3
    FAIL_MOVE = 4
    GIVE_UP = 5


class Game_Service:
    def __init__(self):
        pass

    def best_move_bot(self, game: Current_Game):
        if game.game_board.is_full():
            return
        if game.game_board.is_void():
            game.game_board.board[randint(0, 2)][randint(0, 2)] = Constant.CROSS
            return
        best_move = None
        best_score = -float("inf")
        for i in range(Constant.SIZE):
            for j in range(Constant.SIZE):
                if game.game_board.board[i][j] == Constant.VOID:
                    game.game_board.board[i][j] = Constant.CROSS
                    score = self.minmax(game.game_board, 0, Constant.ZERO)
                    game.game_board.board[i][j] = Constant.VOID
                    if score > best_score:
                        best_score = score
                        best_move = Move(j, i, Constant.CROSS)
        game.game_board.board[best_move.y][best_move.x] = best_move.element

    def minmax(self, board: GameBoard, depth: int, user: Constant):
        game_status = self.evaluate_game_status(board)
        if game_status == Game_Status.DRAW:
            return 0
        elif game_status == Game_Status.WIN_ZERO:
            return -10 + depth
        elif game_status == Game_Status.WIN_CROSS:
            return 10 - depth

        if user == Constant.CROSS:
            best_score = -float("inf")
            for i in range(Constant.SIZE):
                for j in range(Constant.SIZE):
                    if board.get_cell(j, i) == Constant.VOID:
                        board.set_cell(j, i, Constant.CROSS)
                        score = self.minmax(board, depth + 1, Constant.ZERO)
                        board.reset_cell(j, i)
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for i in range(Constant.SIZE):
                for j in range(Constant.SIZE):
                    if board.get_cell(j, i) == Constant.VOID:
                        board.set_cell(j, i, Constant.ZERO)
                        score = self.minmax(board, depth + 1, Constant.CROSS)
                        board.reset_cell(j, i)
                        best_score = min(score, best_score)
            return best_score

    @staticmethod
    def validation(game: Current_Game, move: Move) -> bool:
        return game.game_board.valid_cell(move.x, move.y)

    @staticmethod
    def evaluate_game_status(board: GameBoard) -> Game_Status:
        game_status = board.check_winner()
        if game_status == Constant.VOID:
            for i in range(Constant.SIZE):
                for j in range(Constant.SIZE):
                    if board.get_cell(j, i) == Constant.VOID:
                        return Game_Status.IN_GAME
            return Game_Status.DRAW
        elif game_status == Constant.CROSS:
            return Game_Status.WIN_CROSS
        elif game_status == Constant.ZERO:
            return Game_Status.WIN_ZERO
