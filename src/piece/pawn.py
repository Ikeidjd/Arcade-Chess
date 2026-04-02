from typing import Iterator

import arcade
from .type import PieceType, PieceColor, MarkerPieceType, PiecePos
from .piece import Piece
from board import Board


class Pawn(Piece):
    PROMOTION_RANKS: dict[PieceColor, int] = {
        PieceColor.WHITE: 7,
        PieceColor.BLACK: 0
    }

    INITIAL_RANKS: dict[PieceColor, int] = {
        PieceColor.WHITE: 1,
        PieceColor.BLACK: 6
    }

    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.PAWN, piece_color, piece_pos, board, symmetric_dirs=False)

        self.forward_dir: PiecePos = PiecePos(1, 0) if self.has_color(PieceColor.WHITE) else PiecePos(-1, 0)
        self.capture_dirs: set[PiecePos] = {PiecePos(1, -1), PiecePos(1, 1)} if self.has_color(PieceColor.WHITE) else {PiecePos(-1, -1), PiecePos(-1, 1)}

        self.en_passant: PiecePos | None = None
        self.is_promotion: bool = False

    def remove_move(self, move: PiecePos) -> None:
        super().remove_move(move)

        if self.en_passant == move:
            self.en_passant = None

    def gen_moves(self):
        super().gen_moves()

        if self.try_add_move(self.piece_pos, self.forward_dir, allow_capture=False) and self.piece_pos.rank == self.INITIAL_RANKS[self.piece_color]:
            self.try_add_move(self.piece_pos + self.forward_dir, self.forward_dir, allow_capture=False)

        for dir in self.capture_dirs:
            if self.try_add_move(self.piece_pos, dir, allow_move=False):
                continue

            move = self.piece_pos + dir

            # The en passant position might be occupied by the duck
            if self.board.is_in_bounds(move) and self.board[move] is None and self.board.has_marker(move, MarkerPieceType.EN_PASSANT):
                self.en_passant = move

    def clear_moves(self) -> None:
        super().clear_moves()
        self.en_passant = None
        self.is_promotion = False

    def simulate_moves(self) -> Iterator[PiecePos]:
        for move in super().simulate_moves():
            yield move

        if self.en_passant:
            simulated_move1 = self.do_simulate_move(self.en_passant - self.forward_dir)
            simulated_move2 = self.do_simulate_move(self.en_passant)

            yield self.en_passant

            self.undo_simulate_move(simulated_move2)
            self.undo_simulate_move(simulated_move1)

    def try_move(self, move: PiecePos) -> bool:
        future_en_passant_pos = None

        # Double pawn move adds en passant marker. This has to be checked before super().try_move(board, move) because that method changes self.piece_pos
        if move == self.piece_pos + self.forward_dir * 2:
            future_en_passant_pos = self.piece_pos + self.forward_dir

        if super().try_move(move):
            if move.rank == self.PROMOTION_RANKS[self.piece_color]:
                self.is_promotion = True
            elif future_en_passant_pos:
                self.board.add_marker(future_en_passant_pos, MarkerPieceType.EN_PASSANT)
                self.move_packet.added_markers.append((future_en_passant_pos, MarkerPieceType.EN_PASSANT))

            return True

        if self.en_passant and move == self.en_passant:
            self.capture(self.en_passant - self.forward_dir)
            self.move(self.en_passant)

            return True

        return False

    def end_move_transition(self, view_manager: arcade.Window) -> None:
        super().end_move_transition(view_manager)

        if self.is_promotion:
            from gamestate.chess_normal.promotion import PawnPromotionView
            self.remove_from_sprite_lists()
            assert(view_manager.current_view)
            view_manager.show_view(PawnPromotionView(view_manager.current_view, self.piece_color, self.piece_pos, self.forward_dir, self.move_packet)) # pyright: ignore[reportArgumentType]

    def draw_as_selected(self) -> None:
        if self.en_passant:
            self.draw_capture(self.en_passant)

        super().draw_as_selected()