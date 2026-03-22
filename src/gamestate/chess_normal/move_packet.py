from typing import Any
from piece.type import PieceType, PieceColor, PiecePos


class MovePacket:
    def __init__(self, src_color: PieceColor, start: list[PiecePos] | None = None, end: list[PiecePos] | None = None,
                 captures: list[PiecePos] | None = None, future_en_passant_pos: PiecePos | None = None, promotion_piece: tuple[PieceType, PieceColor] | None = None) -> None:
        self.src_color: PieceColor = src_color
        self.start: list[PiecePos] = [] if start is None else start
        self.end: list[PiecePos] = [] if end is None else end
        self.captures: list[PiecePos] | None = captures
        self.future_en_passant_pos: PiecePos | None = future_en_passant_pos
        self.promotion_piece: tuple[PieceType, PieceColor] | None = promotion_piece

    def to_dict(self) -> dict[str, Any]:
        return {
            "src_color": self.src_color.value,
            "start": [(pos.rank, pos.file) for pos in self.start],
            "end": [(pos.rank, pos.file) for pos in self.end],
            "captures": self.captures if self.captures is None else [(pos.rank, pos.file) for pos in self.captures],
            "future_en_passant_pos": self.future_en_passant_pos if self.future_en_passant_pos is None else (self.future_en_passant_pos.rank, self.future_en_passant_pos.file),
            "promotion_piece": self.promotion_piece if self.promotion_piece is None else (self.promotion_piece[0].value, self.promotion_piece[1].value)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MovePacket":
        return cls(
            PieceColor(data["src_color"]),
            [PiecePos(rank, file) for rank, file in data["start"]],
            [PiecePos(rank, file) for rank, file in data["end"]],
            data["captures"] if data["captures"] is None else [PiecePos(rank, file) for rank, file in data["captures"]],
            data["future_en_passant_pos"] if data["future_en_passant_pos"] is None else PiecePos(*data["future_en_passant_pos"]),
            data["promotion_piece"] if data["promotion_piece"] is None else (PieceType(data["promotion_piece"][0]), PieceColor(data["promotion_piece"][1]))
        )