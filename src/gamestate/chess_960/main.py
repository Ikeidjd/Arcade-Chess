from copy import deepcopy
import random
from constants import BOARD_SIZE
from board import Board
from gamestate.chess_normal.main import ChessNormalMainView
from piece.type import PieceColor


# TODO: change castling rules
class Chess960MainView(ChessNormalMainView):
    def __init__(self) -> None:
        ChessNormalMainView.__init__(self, self.randomize_initial_board())

    def randomize_initial_board(self) -> list[list[str]]:
        initial_board = deepcopy(self.initial_board)

        available_files = list(range(BOARD_SIZE))

        b1 = self.random_file(available_files, 0)
        b2 = self.random_file(available_files, 1)

        n1 = self.random_file(available_files)
        n2 = self.random_file(available_files)

        q = self.random_file(available_files)

        r1, k, r2 = tuple(available_files)

        initial_board[0][b1] = "BB"
        initial_board[0][b2] = "BB"
        initial_board[0][n1] = "NB"
        initial_board[0][n2] = "NB"
        initial_board[0][q] = "QB"
        initial_board[0][r1] = "RB"
        initial_board[0][k] = "KB"
        initial_board[0][r2] = "RB"

        initial_board[7][b1] = "BW"
        initial_board[7][b2] = "BW"
        initial_board[7][n1] = "NW"
        initial_board[7][n2] = "NW"
        initial_board[7][q] = "QW"
        initial_board[7][r1] = "RW"
        initial_board[7][k] = "KW"
        initial_board[7][r2] = "RW"

        return initial_board

    @staticmethod
    def random_file(available_files: list[int], parity: int | None = None) -> int:
        out = random.choice(available_files)

        while parity is not None and out % 2 != parity:
            out = random.choice(available_files)

        available_files.remove(out)
        return out