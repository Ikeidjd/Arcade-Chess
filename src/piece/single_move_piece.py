from .type import PieceType, PieceColor, PiecePos
from .piece import Piece
from board import Board


class SingleMovePiece(Piece):
    def __init__(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece], dirs: set[PiecePos]) -> None:
        super().__init__(piece_type, piece_color, piece_pos, board, dirs)

    def gen_moves(self, can_castle_kingside: bool, can_castle_queenside: bool) -> None:
        super().gen_moves(can_castle_kingside, can_castle_queenside)

        for dir in self.dirs:
            self.try_add_move(self.piece_pos, dir)