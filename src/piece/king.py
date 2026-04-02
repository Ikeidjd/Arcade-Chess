from typing import Iterator

import arcade
from enum import Enum, auto
from piece.piece import Piece
from piece.rook import Rook
from piece.type import PieceType, PieceColor, PiecePos
from .single_move_piece import SingleMovePiece
from board import Board


class CastleType(Enum):
    KINGSIDE = auto()
    QUEENSIDE = auto()


class King(SingleMovePiece):
    CASTLE_DIRS: dict[CastleType, PiecePos] = {
        CastleType.KINGSIDE: PiecePos(0, 1),
        CastleType.QUEENSIDE: PiecePos(0, -1)
    }

    CASTLE_TARGETS: dict[CastleType, dict[PieceColor, dict[PieceType, PiecePos]]] = {
        CastleType.KINGSIDE: {
            PieceColor.WHITE: {
                PieceType.ROOK: PiecePos(0, 5),
                PieceType.KING: PiecePos(0, 6)
            },
            PieceColor.BLACK: {
                PieceType.ROOK: PiecePos(7, 5),
                PieceType.KING: PiecePos(7, 6)
            }
        },
        CastleType.QUEENSIDE: {
            PieceColor.WHITE: {
                PieceType.ROOK: PiecePos(0, 3),
                PieceType.KING: PiecePos(0, 2)
            },
            PieceColor.BLACK: {
                PieceType.ROOK: PiecePos(7, 3),
                PieceType.KING: PiecePos(7, 2)
            }
        }
    }

    def __init__(self, piece_color: PieceColor, piece_pos: PiecePos, board: Board[Piece]) -> None:
        super().__init__(PieceType.KING, piece_color, piece_pos, board, {PiecePos(0, 1), PiecePos(1, 1)})

        self.can_castle: bool = True

        self.castle_moves: dict[CastleType, PiecePos | None] = {
            CastleType.KINGSIDE: None,
            CastleType.QUEENSIDE: None
        }

        self.castle_rooks: dict[CastleType, Rook | None] = {
            CastleType.KINGSIDE: None,
            CastleType.QUEENSIDE: None
        }

        self.move_transition_rook: Rook | None = None

    def remove_move(self, move: PiecePos) -> None:
        super().remove_move(move)

        if move == self.castle_moves[CastleType.KINGSIDE]:
            self.castle_moves[CastleType.KINGSIDE] = None
        elif move == self.castle_moves[CastleType.QUEENSIDE]:
            self.castle_moves[CastleType.QUEENSIDE] = None

    def gen_moves(self) -> None:
        super().gen_moves()

        self.try_add_castle(CastleType.KINGSIDE)
        self.try_add_castle(CastleType.QUEENSIDE)

    def try_add_castle(self, castle_type: CastleType) -> None:
        if not self.can_castle:
            return

        castle_dir = self.CASTLE_DIRS[castle_type]

        if (rook := self.get_rook_for_castle(castle_dir)) is None:
            return

        castle_target_king = self.CASTLE_TARGETS[castle_type][self.piece_color][PieceType.KING]
        castle_target_rook = self.CASTLE_TARGETS[castle_type][self.piece_color][PieceType.ROOK]

        self.board[rook.piece_pos] = None
        can_castle = self.check_empty_squares_for_castle(self.piece_pos, castle_target_king)
        self.board[rook.piece_pos] = rook

        self.board[self.piece_pos] = None
        can_castle = can_castle and self.check_empty_squares_for_castle(rook.piece_pos, castle_target_rook)
        self.board[self.piece_pos] = self

        if can_castle:
            # Makes the castle move show up on the rook itself in 960 chess (unless the position of the king is the same as in normal chess)
            self.castle_moves[castle_type] = castle_target_king if self.piece_pos.manhattan_distance(castle_target_king) == 2 else rook.piece_pos
            self.castle_rooks[castle_type] = rook

    def get_rook_for_castle(self, castle_dir: PiecePos) -> Rook | None:
        pos = self.piece_pos + castle_dir

        try:
            while (rook := self.board[pos]) is None:
                pos += castle_dir
        except IndexError:
            return None
        else:
            if self.is_friend(rook) and isinstance(rook, Rook) and rook.can_castle:
                return rook

            return None

    def check_empty_squares_for_castle(self, start: PiecePos, target: PiecePos) -> bool:
        dir = (target - start).normalize()

        if dir == PiecePos(0, 0):
            return True

        pos = start + dir

        while pos != target and self.board[pos] is None:
            pos += dir

        if self.has_color(PieceColor.WHITE):
            print(start, target, pos, dir)
        return pos == target and self.board[pos] is None

    def clear_moves(self) -> None:
        super().clear_moves()

        self.castle_moves[CastleType.KINGSIDE] = None
        self.castle_moves[CastleType.QUEENSIDE] = None

        self.castle_rooks[CastleType.KINGSIDE] = None
        self.castle_rooks[CastleType.QUEENSIDE] = None

        self.move_transition_rook = None

    def simulate_moves(self) -> Iterator[PiecePos]:
        for move in super().simulate_moves():
            yield move

        for move in self.simulate_castle(CastleType.KINGSIDE):
            yield move

        for move in self.simulate_castle(CastleType.QUEENSIDE):
            yield move

    def simulate_castle(self, castle_type: CastleType) -> Iterator[PiecePos]:
        if (move := self.castle_moves[castle_type]) is None:
            return

        assert(rook := self.castle_rooks[castle_type])

        self.board[rook.piece_pos] = None
        rook_pos = rook.piece_pos
        rook.piece_pos = PiecePos.out_of_bounds()

        dir = (move - self.piece_pos).normalize()
        pos = self.piece_pos

        while True:
            simulated_move = self.do_simulate_move(pos)
            yield move
            self.undo_simulate_move(simulated_move)

            if pos == move:
                break

            pos += dir

        rook.piece_pos = rook_pos
        self.board[rook.piece_pos] = rook

    def try_move(self, move: PiecePos) -> bool:
        if super().try_move(move) or self.try_move_castle(move, CastleType.KINGSIDE) or self.try_move_castle(move, CastleType.QUEENSIDE):
            self.can_castle = False
            return True

        return False

    def try_move_castle(self, move: PiecePos, castle_type: CastleType) -> bool:
        castle_move = self.castle_moves[castle_type]
        castle_rook = self.castle_rooks[castle_type]

        castle_target_king = self.CASTLE_TARGETS[castle_type][self.piece_color][PieceType.KING]
        castle_target_rook = self.CASTLE_TARGETS[castle_type][self.piece_color][PieceType.ROOK]

        if castle_move and move == castle_move:
            assert(castle_rook)

            self.move(castle_target_king)

            self.move_packet.start.append(castle_rook.piece_pos)
            self.move_packet.end.append(castle_target_rook)

            castle_rook.move(castle_target_rook)
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
        self.draw_castle(CastleType.KINGSIDE)
        self.draw_castle(CastleType.QUEENSIDE)

        super().draw_as_selected()

    def draw_castle(self, castle_type: CastleType) -> None:
        if castle := self.castle_moves[castle_type]:
            self.draw_move(castle)