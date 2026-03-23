from piece.type import PieceColor
from gamestate.chess_normal.online import ChessNormalOnlineView
from .main import ChessAtomicMainView


class ChessAtomicOnlineView(ChessNormalOnlineView, ChessAtomicMainView):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        super().__init__(my_turn_color, is_host, host, port)

    def on_fully_ended_move(self, /, call_super: bool = False) -> None:
        ChessAtomicMainView.on_fully_ended_move(self, call_super=call_super)
        ChessNormalOnlineView.on_fully_ended_move(self)