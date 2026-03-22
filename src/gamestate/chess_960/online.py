from typing import Any
from PodSixNet.Connection import ConnectionListener, connection
from board import Board
from gamestate.chess_normal.online import ChessNormalOnlineView
from piece.type import PieceColor
from .main import Chess960MainView


class Chess960OnlineView(Chess960MainView, ChessNormalOnlineView):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        Chess960MainView.__init__(self)
        ChessNormalOnlineView.__init__(self, my_turn_color, is_host, host, port)

    def Network_start_game(self, data: dict[str, Any]) -> None:
        if self.server:
            connection.Send({"action": "initial_board", "initial_board": self.initial_board})

    def Network_initial_board(self, data: dict[str, Any]) -> None:
        self.board.fill(data["initial_board"])
        self.gen_moves()
        self.start_game = True