from .type import *
from .piece import Piece
from .pawn import Pawn
from .single_move_piece import SingleMovePiece
from .looping_move_piece import LoopingMovePiece
from .rook import Rook
from .king import King


def new(name: str, piece_pos: PiecePos) -> Piece:
    piece_type = piece_type_from_str[name[0]]
    piece_color = piece_color_from_str[name[1]]

    match piece_type:
        case PieceType.PAWN:
            return Pawn(piece_color, piece_pos)
        case PieceType.KNIGHT:
            return SingleMovePiece(piece_type, piece_color, piece_pos, {PiecePos(1, 2)})
        case PieceType.BISHOP:
            return LoopingMovePiece(piece_type, piece_color, piece_pos, {PiecePos(1, 1)})
        case PieceType.ROOK:
            return Rook(piece_color, piece_pos)
        case PieceType.QUEEN:
            return LoopingMovePiece(piece_type, piece_color, piece_pos, {PiecePos(0, 1), PiecePos(1, 1)})
        case PieceType.KING:
            return King(piece_color, piece_pos)