from .type import PieceType, PieceColor, PiecePos
from .piece import Piece


class Pawn(Piece):
    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos) -> None:
        super().__init__(PieceType.PAWN, piece_color, piece_pos, symmetric_dirs=False)

        self.start_pos: PiecePos = self.piece_pos
        self.en_passant_capture: PiecePos | None = None

        self.forward_dir: PiecePos = PiecePos(1, 0) if self.has_color(PieceColor.WHITE) else PiecePos(-1, 0)
        self.capture_dirs: set[PiecePos] = {PiecePos(1, -1), PiecePos(1, 1)} if self.has_color(PieceColor.WHITE) else {PiecePos(-1, -1), PiecePos(-1, 1)}

    def gen_moves(self, board: list[list[Piece | None]], en_passant: tuple[PiecePos, PieceColor] | None, can_castle_kingside: bool, can_castle_queenside: bool):
        super().gen_moves(board, en_passant, can_castle_kingside, can_castle_queenside)

        if self.try_add_move(board, self.piece_pos, self.forward_dir, allow_capture=False) and self.piece_pos.rank == self.start_pos.rank:
            self.try_add_move(board, self.piece_pos + self.forward_dir, self.forward_dir, allow_capture=False)

        self.en_passant_capture = None

        for dir in self.capture_dirs:
            self.try_add_move(board, self.piece_pos, dir, allow_move=False)

            if not en_passant:
                continue

            move = self.piece_pos + dir
            en_passant_pos, en_passant_color = en_passant
            if move == en_passant_pos and not self.has_color(en_passant_color):
                self.en_passant_capture = move

    def clear_moves(self) -> None:
        super().clear_moves()
        self.en_passant_capture = None

    def try_move(self, board: list[list[Piece | None]], move: PiecePos) -> Piece.MoveResult:
        future_en_passant = None

        # Double pawn move notifies of possible future en passant. This has to be checked before super().try_move(board, move) because that method changes self.piece_pos
        if move == self.piece_pos + self.forward_dir * 2:
            future_en_passant = self.piece_pos + self.forward_dir, self.piece_color

        move_result = super().try_move(board, move)

        if move_result.did_move:
            move_result.future_en_passant = future_en_passant
            return move_result

        if self.en_passant_capture and move == self.en_passant_capture:
            self.capture(board, self.en_passant_capture - self.forward_dir)
            self.move(board, move)
            return self.MoveResult(True)

        return self.MoveResult(False)

    def draw_as_selected(self) -> None:
        if self.en_passant_capture:
            self.draw_capture(self.en_passant_capture)

        super().draw_as_selected()