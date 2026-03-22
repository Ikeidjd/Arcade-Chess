import arcade
from piece.piece import Piece
from piece.type import PieceType, PieceColor, PiecePos
from .single_move_piece import SingleMovePiece
from board import Board


class King(SingleMovePiece):
    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.KING, piece_color, piece_pos, board, {PiecePos(0, 1), PiecePos(1, 1)})

        self.kingside_rook: Piece | None = None
        self.queenside_rook: Piece | None = None
        self.move_transition_rook: Piece | None = None

        self.castle_kingside: PiecePos | None = None
        self.castle_queenside: PiecePos | None = None

        self.kingside_dir: PiecePos = PiecePos(0, 1) if self.has_color(PieceColor.WHITE) else PiecePos(0, -1)
        self.queenside_dir: PiecePos = PiecePos(0, -1) if self.has_color(PieceColor.WHITE) else PiecePos(0, 1)

    def gen_moves(self, possible_en_passant_pos: PiecePos | None, can_castle_kingside: bool, can_castle_queenside: bool) -> None:
        super().gen_moves(possible_en_passant_pos, can_castle_kingside, can_castle_queenside)

        self.castle_kingside, self.kingside_rook = self.try_gen_castle(self.kingside_dir, can_castle_kingside)
        self.castle_queenside, self.queenside_rook = self.try_gen_castle(self.queenside_dir, can_castle_queenside)

    def try_gen_castle(self, castle_dir: PiecePos, can_castle: bool) -> tuple[PiecePos, Piece] | tuple[None, None]:
            if not can_castle:
                return None, None

            pos = self.piece_pos + castle_dir
            try:
                while (rook := self.board[pos]) is None:
                    pos += castle_dir
            except IndexError:
                return None, None
            else:
                if rook.has_type(PieceType.ROOK):
                    return self.piece_pos + castle_dir * 2, rook

                return None, None

    def clear_moves(self) -> None:
        super().clear_moves()
        self.kingside_rook = self.queenside_rook = self.move_transition_rook = self.castle_kingside = self.castle_queenside = None

    def try_move(self, move: PiecePos) -> Piece.MoveResult:
        move_result = super().try_move(move)
        move_result.disable_kingside_castle = move_result.disable_queenside_castle = True

        if not move_result.did_move:
            move_result.did_move = self.try_move_castle(move, self.castle_kingside, self.kingside_rook, self.kingside_dir)

        if not move_result.did_move:
            move_result.did_move = self.try_move_castle(move, self.castle_queenside, self.queenside_rook, self.queenside_dir)

        return move_result

    def try_move_castle(self, move: PiecePos, castle_move: PiecePos | None, castle_rook: Piece | None, castle_dir: PiecePos) -> bool:
        if castle_move and move == castle_move:
            self.move(move)

            assert(castle_rook)

            self.move_packet.start.append(castle_rook.piece_pos)
            self.move_packet.end.append(move - castle_dir)

            castle_rook.move(move - castle_dir)
            self.move_transition_rook = castle_rook

            return True

        return False

    def advance_move_transition(self, delta_time: float, view_manager: arcade.Window) -> None:
        super().advance_move_transition(delta_time, view_manager)

        if self.move_transition_rook:
            self.move_transition_rook.advance_move_transition(delta_time, view_manager)
            self.moving = self.move_transition_rook.moving
            self.just_finished_moving = self.move_transition_rook.just_finished_moving

            if self.move_transition_rook.just_finished_moving:
                self.move_transition_rook.fully_end_move_transition()

    def draw_as_selected(self) -> None:
        if self.castle_kingside:
            self.draw_move(self.castle_kingside)

        if self.castle_queenside:
            self.draw_move(self.castle_queenside)

        super().draw_as_selected()