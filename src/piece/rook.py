from piece.piece import Piece
from piece.type import PieceColor, PiecePos, PieceType
from .looping_move_piece import LoopingMovePiece
from board import Board


class Rook(LoopingMovePiece):
    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.ROOK, piece_color, piece_pos, board, {PiecePos(0, 1)})
        self.can_castle: bool = True

    def try_move(self, move: PiecePos) -> bool:
        if super().try_move(move):
            self.can_castle = False
            return True

        return False