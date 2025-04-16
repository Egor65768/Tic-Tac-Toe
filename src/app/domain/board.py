class Constant:
    SIZE = 3
    VOID = 0
    CROSS = 1
    ZERO = 2


class GameBoard:
    def __init__(self, size: int = Constant.SIZE, board: list = None):
        self.size = size
        self.board = (
            [[Constant.VOID for _ in range(self.size)] for _ in range(self.size)]
            if board is None
            else board
        )

    def valid_coordinates(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def valid_cell(self, x: int, y: int) -> bool:
        return self.valid_coordinates(x, y) and self.get_cell(x, y) == Constant.VOID

    def get_cell(self, x: int, y: int):
        if self.valid_coordinates(x, y):
            return self.board[y][x]
        return None

    def set_cell(self, x: int, y: int, symbol: int) -> bool:
        if self.valid_cell(x, y):
            self.board[y][x] = symbol
            return True
        return False

    def reset_cell(self, x: int, y: int):
        if self.valid_coordinates(x, y):
            self.board[y][x] = Constant.VOID

    def check_winner(self):
        for x in range(Constant.SIZE):
            if self.get_cell(x, 0) != Constant.VOID and self.get_cell(
                x, 0
            ) == self.get_cell(x, 1) == self.get_cell(x, 2):
                return self.get_cell(x, 0)
        for y in range(Constant.SIZE):
            if self.get_cell(0, y) != Constant.VOID and self.get_cell(
                0, y
            ) == self.get_cell(1, y) == self.get_cell(2, y):
                return self.get_cell(0, y)
        if self.get_cell(0, 0) != Constant.VOID and self.get_cell(
            0, 0
        ) == self.get_cell(1, 1) == self.get_cell(2, 2):
            return self.get_cell(0, 0)
        if self.get_cell(2, 0) != Constant.VOID and self.get_cell(
            2, 0
        ) == self.get_cell(1, 1) == self.get_cell(0, 2):
            return self.get_cell(2, 0)
        return Constant.VOID

    def is_full(self):
        for line in self.board:
            for cell in line:
                if cell == Constant.VOID:
                    return False
        return True

    def is_void(self):
        for line in self.board:
            for cell in line:
                if cell != Constant.VOID:
                    return False
        return True
