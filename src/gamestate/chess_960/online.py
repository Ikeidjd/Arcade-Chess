from typing import Any
from PodSixNet.Connection import connection
from piece.type import PieceColor
from gamestate.chess_normal.online import ChessNormalOnlineView
from .main import Chess960MainView


class Chess960OnlineView(ChessNormalOnlineView, Chess960MainView):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        super().__init__(my_turn_color, is_host, host, port)

    def Network_start_game(self, data: dict[str, Any]) -> None:
        if self.server:
            connection.Send({"action": "initial_board", "initial_board": self.initial_board})

    def Network_initial_board(self, data: dict[str, Any]) -> None:
        self.board.fill(data["initial_board"])
        self.gen_moves()
        self.start_game = True