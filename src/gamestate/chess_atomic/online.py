from piece.type import PieceColor
from gamestate.chess_normal.online import ChessNormalOnlineView
from .main import ChessAtomicMainView


class ChessAtomicOnlineView(ChessAtomicMainView, ChessNormalOnlineView):
    def __init__(self, my_turn_color: PieceColor, is_host: bool, host: str, port: int) -> None:
        ChessAtomicMainView.__init__(self)
        ChessNormalOnlineView.__init__(self, my_turn_color, is_host, host, port)