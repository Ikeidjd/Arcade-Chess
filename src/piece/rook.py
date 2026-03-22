from piece.piece import Piece
from piece.type import PieceColor, PiecePos, PieceType
from .looping_move_piece import LoopingMovePiece
from board import Board


class Rook(LoopingMovePiece):
    KINGSIDE_ROOK_POS = {
        PieceColor.WHITE: PiecePos(0, 7),
        PieceColor.BLACK: PiecePos(7, 0)
    }

    QUEENSIDE_ROOK_POS = {
        PieceColor.WHITE: PiecePos(0, 0),
        PieceColor.BLACK: PiecePos(7, 7)
    }

    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.ROOK, piece_color, piece_pos, board, {PiecePos(0, 1)})

    def try_move(self, move: PiecePos) -> Piece.MoveResult:
        # This has to go before super().try_move(board, move) because that method changes self.piece_pos
        disable_kingside_castle = self.piece_pos == self.KINGSIDE_ROOK_POS[self.piece_color]
        disable_queenside_castle = self.piece_pos == self.QUEENSIDE_ROOK_POS[self.piece_color]

        move_result = super().try_move(move)
        move_result.disable_kingside_castle = disable_kingside_castle
        move_result.disable_queenside_castle = disable_queenside_castle

        return move_result