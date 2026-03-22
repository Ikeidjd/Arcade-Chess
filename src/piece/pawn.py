import arcade
from .type import PieceType, PieceColor, PiecePos
from .piece import Piece
from board import Board


class Pawn(Piece):
    PROMOTION_RANKS = {
        PieceColor.WHITE: 7,
        PieceColor.BLACK: 0
    }

    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.PAWN, piece_color, piece_pos, board, symmetric_dirs=False)

        self.start_pos: PiecePos = self.piece_pos
        self.en_passant_capture: PiecePos | None = None

        self.forward_dir: PiecePos = PiecePos(1, 0) if self.has_color(PieceColor.WHITE) else PiecePos(-1, 0)
        self.capture_dirs: set[PiecePos] = {PiecePos(1, -1), PiecePos(1, 1)} if self.has_color(PieceColor.WHITE) else {PiecePos(-1, -1), PiecePos(-1, 1)}

        self.is_promotion: bool = False

    def gen_moves(self, possible_en_passant_pos: PiecePos | None, can_castle_kingside: bool, can_castle_queenside: bool):
        super().gen_moves(possible_en_passant_pos, can_castle_kingside, can_castle_queenside)

        if self.try_add_move(self.piece_pos, self.forward_dir, allow_capture=False) and self.piece_pos.rank == self.start_pos.rank:
            self.try_add_move(self.piece_pos + self.forward_dir, self.forward_dir, allow_capture=False)

        self.en_passant_capture = None

        for dir in self.capture_dirs:
            self.try_add_move(self.piece_pos, dir, allow_move=False)

            if not possible_en_passant_pos:
                continue

            move = self.piece_pos + dir
            if move == possible_en_passant_pos:
                self.en_passant_capture = move

    def clear_moves(self) -> None:
        super().clear_moves()
        self.en_passant_capture = None
        self.is_promotion = False

    def try_move(self, move: PiecePos) -> Piece.MoveResult:
        future_en_passant_pos = None

        # Double pawn move notifies of possible future en passant. This has to be checked before super().try_move(board, move) because that method changes self.piece_pos
        if move == self.piece_pos + self.forward_dir * 2:
            future_en_passant_pos = self.piece_pos + self.forward_dir

        move_result = super().try_move(move)

        if move_result.did_move:
            if move.rank == self.PROMOTION_RANKS[self.piece_color]:
                self.is_promotion = True

            self.move_packet.future_en_passant_pos = future_en_passant_pos
            move_result.future_en_passant_pos = future_en_passant_pos
            return move_result

        if self.en_passant_capture and move == self.en_passant_capture:
            self.capture(self.en_passant_capture - self.forward_dir)
            self.move(move)
            return self.MoveResult(True)

        return self.MoveResult(False)

    def end_move_transition(self, view_manager: arcade.Window) -> None:
        super().end_move_transition(view_manager)

        if self.is_promotion:
            from gamestate.normal_chess.promotion import NormalChessPromotionView
            self.remove_from_sprite_lists()
            view_manager.show_view(NormalChessPromotionView(view_manager.current_view, self.piece_color, self.piece_pos, self.forward_dir, self.move_packet)) # type: ignore

    def draw_as_selected(self) -> None:
        if self.en_passant_capture:
            self.draw_capture(self.en_passant_capture)

        super().draw_as_selected()