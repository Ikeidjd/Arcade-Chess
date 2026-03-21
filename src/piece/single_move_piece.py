from .type import PieceType, PieceColor, PiecePos
from .piece import Piece


class SingleMovePiece(Piece):
    def __init__(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, dirs: set[PiecePos]) -> None:
        super().__init__(piece_type, piece_color, piece_pos, dirs)

    def gen_moves(self, board: list[list[Piece | None]], en_passant: tuple[PiecePos, PieceColor] | None, can_castle_kingside: bool, can_castle_queenside: bool) -> None:
        super().gen_moves(board, en_passant, can_castle_kingside, can_castle_queenside)

        for dir in self.dirs:
            self.try_add_move(board, self.piece_pos, dir)