from enum import Enum, auto
from dataclasses import dataclass


class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()


class PieceColor(Enum):
    WHITE = auto()
    BLACK = auto()
    DUCK = auto()


class MarkerPieceType(Enum):
    EN_PASSANT = auto()


@dataclass(unsafe_hash=True)
class PiecePos:
    rank: int
    file: int

    def copy(self) -> "PiecePos":
        return PiecePos(self.rank, self.file)

    def normalize(self) -> "PiecePos":
        out = self.copy()

        if out.rank > 0:
            out.rank = 1
        elif out.rank < 0:
            out.rank = -1

        if out.file > 0:
            out.file = 1
        elif out.file < 0:
            out.file = -1

        return out

    def manhattan_distance(self, other: "PiecePos") -> int:
        return abs(self.rank - other.rank) + abs(self.file - other.file)

    def __add__(self, other: "PiecePos") -> "PiecePos":
        return PiecePos(self.rank + other.rank, self.file + other.file)

    def __sub__(self, other: "PiecePos") -> "PiecePos":
        return PiecePos(self.rank - other.rank, self.file - other.file)

    def __neg__(self) -> "PiecePos":
        return PiecePos(-self.rank, -self.file)

    def __mul__(self, num: int) -> "PiecePos":
        return PiecePos(self.rank * num, self.file * num)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PiecePos) and self.rank == other.rank and self.file == other.file

    def __repr__(self) -> str:
        return f"PiecePos({self.rank}, {self.file})"

    @classmethod
    def out_of_bounds(cls) -> "PiecePos":
        return cls(-2, -2)


piece_type_from_str = {
    'P': PieceType.PAWN,
    'N': PieceType.KNIGHT,
    'B': PieceType.BISHOP,
    'R': PieceType.ROOK,
    'Q': PieceType.QUEEN,
    'K': PieceType.KING
}


piece_color_from_str = {
    'W': PieceColor.WHITE,
    'B': PieceColor.BLACK
}


_piece_sprite_paths = {
    PieceColor.WHITE: {
        PieceType.PAWN: "res/pawn.png",
        PieceType.KNIGHT: "res/knight.png",
        PieceType.BISHOP: "res/bishop.png",
        PieceType.ROOK: "res/rook.png",
        PieceType.QUEEN: "res/queen.png",
        PieceType.KING: "res/king.png"
    },
    PieceColor.BLACK: {
        PieceType.PAWN: "res/pawn_black.png",
        PieceType.KNIGHT: "res/knight_black.png",
        PieceType.BISHOP: "res/bishop_black.png",
        PieceType.ROOK: "res/rook_black.png",
        PieceType.QUEEN: "res/queen_black.png",
        PieceType.KING: "res/king_black.png"
    },
    PieceColor.DUCK: {
        PieceType.PAWN: "res/duck.png"
    }
}

def get_piece_sprite_path(piece_type: PieceType, piece_color: PieceColor) -> str:
    if piece_color not in _piece_sprite_paths.keys() or piece_type not in _piece_sprite_paths[piece_color].keys():
        return "res/missing_texture.png"

    return _piece_sprite_paths[piece_color][piece_type]