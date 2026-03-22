from enum import Enum, auto


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


class PiecePos:
    def __init__(self, rank: int, file: int) -> None:
        self.rank = rank
        self.file = file

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

    def __hash__(self) -> int:
        return hash((self.rank << 32) & self.file)


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


piece_sprite_paths = {
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
    }
}