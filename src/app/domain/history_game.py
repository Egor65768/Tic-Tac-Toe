from datetime import datetime


class Constant:
    WIN = 0
    LOSE = 1
    DRAW = 2


class History_Game:
    def __init__(
        self,
        timestamp: datetime,
        game_was_over: bool,
        opponent: str,
        result: int,
        board: list = None,
    ):
        self.timestamp = timestamp
        self.game_was_over = game_was_over
        self.opponent = opponent
        self.result = result
        self.board = board


class All_History_Game:
    def __init__(
        self, timestamp: datetime, game_was_over: bool, user1, user2, result: int
    ):
        self.timestamp = timestamp
        self.game_was_over = game_was_over
        self.user_1 = user1
        self.user_2 = user2
        self.result = result
