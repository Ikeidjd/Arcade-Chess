from typing import Any

from piece.type import PieceColor, PiecePos
from gamestate.chess_normal.online import ChessNormalOnlineView
from .main import ChessDuckMainView


class ChessDuckOnlineView(ChessNormalOnlineView, ChessDuckMainView):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        super().__init__(my_turn_color, is_host, host, port)

    def on_fully_ended_move(self) -> None:
        ChessDuckMainView.on_fully_ended_move(self)

    def on_fully_ended_duck_move(self, call_super: bool = False) -> None:
        ChessDuckMainView.on_fully_ended_duck_move(self, call_super=call_super)
        ChessNormalOnlineView.on_fully_ended_move(self)

    def Network_move(self, data: dict[str, Any]) -> None:
        duck_n = -1
        duck_start = (-1, -1)
        duck_end = (-1, -1)

        for n, (start, end) in enumerate(zip(data["move"]["start"], data["move"]["end"])):
            if start == (self.duck.piece_pos.rank, self.duck.piece_pos.file):
                duck_n = n
                duck_start = start
                duck_end = end

        data["move"]["start"].pop(duck_n)
        data["move"]["end"].pop(duck_n)

        super().Network_move(data)

        self.duck.move(PiecePos(*duck_end))
        self.enemy_pieces_moving.append(self.duck)

        self.duck_move_start = PiecePos(*duck_start)
        self.duck_move_end = PiecePos(*duck_end)