import arcade
from typing import Iterator
from dataclasses import dataclass
from constants import PIECE_SCALE, PIECE_SIZE, BOARD_SIZE, SCREEN_SIZE
from gamestate.chess_normal.move_packet import MovePacket
import piece.type
from .type import PieceType, PieceColor, MarkerPieceType, PiecePos
from board import Board


class Piece(arcade.Sprite):
    move_transition_length_in_seconds = 0.125

    def __init__(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, board: Board["Piece"], dirs: set[PiecePos] | None = None, *, symmetric_dirs: bool = True) -> None:
        self.piece_type: PieceType = piece_type
        self.piece_color: PieceColor = piece_color
        self.piece_pos: PiecePos = piece_pos

        super().__init__(piece.type.get_piece_sprite_path(self.piece_type, self.piece_color), PIECE_SCALE)
        self.reset_pos()

        if dirs:
            self.dirs: set[PiecePos] = dirs
        else:
            self.dirs: set[PiecePos] = set()

        if symmetric_dirs:
            self.make_dirs_symmetric()

        self.board: Board[Piece] = board

        self.moves: set[PiecePos] = set()
        self.captures: set[PiecePos] = set()
        self.illegal_moves: set[PiecePos] = set()

        self.move_packet: MovePacket = MovePacket(self.piece_color)

        self.moving: bool = False
        self.just_finished_moving: bool = False

        self.start: arcade.Vec2 = arcade.Vec2(0, 0)
        self.target: arcade.Vec2 = arcade.Vec2(0, 0)

    def make_dirs_symmetric(self) -> None:
        dirs: set[PiecePos] = set()

        for dir in self.dirs:
            dirs.add(PiecePos(dir.rank, dir.file))
            dirs.add(PiecePos(-dir.rank, dir.file))
            dirs.add(PiecePos(dir.rank, -dir.file))
            dirs.add(PiecePos(-dir.rank, -dir.file))
            dirs.add(PiecePos(dir.file, dir.rank))
            dirs.add(PiecePos(-dir.file, dir.rank))
            dirs.add(PiecePos(dir.file, -dir.rank))
            dirs.add(PiecePos(-dir.file, -dir.rank))

        self.dirs = dirs

    # Returns true if a move (not capture) was possible
    def try_add_move(self, pos: PiecePos, dir: PiecePos, *, allow_move: bool = True, allow_capture: bool = True) -> bool:
        move = pos + dir
        try:
            piece = self.board[move]
        except IndexError:
            return False
        else:
            if piece is None:
                if allow_move and not self.board.has_marker(move, MarkerPieceType.EN_PASSANT_CASTLE):
                    self.moves.add(move)
                    return True

                if allow_capture and self.board.has_marker(move, MarkerPieceType.EN_PASSANT_CASTLE):
                    self.captures.add(move)

                return False

            if allow_capture and self.is_enemy(piece):
                self.captures.add(move)

            return False

    def add_illegal_move(self, move: PiecePos, *, allow_illegal_moves: bool) -> None:
        if allow_illegal_moves:
            self.illegal_moves.add(move)
        else:
            self.remove_move(move)

    def remove_move(self, move: PiecePos) -> None:
        self.moves.discard(move)
        self.captures.discard(move)

    def gen_moves(self) -> None:
        self.clear_moves()
        self.move_packet = MovePacket(self.piece_color)

    def clear_moves(self) -> None:
        self.moves = set()
        self.captures = set()
        self.illegal_moves = set()

    def simulate_moves(self) -> Iterator[PiecePos]:
        for move in self.moves.union(self.captures):
            simulated_move = self.do_simulate_move(move)
            yield move
            self.undo_simulate_move(simulated_move)

    @dataclass
    class SimulatedMove:
        my_piece_pos: PiecePos
        move: PiecePos
        old_piece: "Piece | None"

    def do_simulate_move(self, move: PiecePos) -> SimulatedMove:
        my_piece_pos = self.piece_pos
        self.piece_pos = move

        old_piece = self.board[move]
        if old_piece:
            old_piece.piece_pos = PiecePos.out_of_bounds()

        self.board[my_piece_pos] = None
        self.board[move] = self

        return self.SimulatedMove(my_piece_pos, move, old_piece)

    def undo_simulate_move(self, simulated_move: SimulatedMove) -> None:
        self.piece_pos = simulated_move.my_piece_pos
        self.board[self.piece_pos] = self

        if simulated_move.old_piece:
            self.board[simulated_move.move] = simulated_move.old_piece
            simulated_move.old_piece.piece_pos = simulated_move.move
        else:
            self.board[simulated_move.move] = None

    def gives_check(self) -> bool:
        for capture in self.captures:
            if (victim := self.board[capture]) and victim.has_type(PieceType.KING):
                return True

        return False

    def try_move(self, move: PiecePos) -> bool:
        can_move = move in self.moves
        can_capture = move in self.captures

        if can_move or can_capture:
            if can_capture:
                self.capture(move)

            self.move(move)

            return True

        return False

    def move(self, move: PiecePos) -> None:
        self.move_packet.start.append(self.piece_pos)
        self.move_packet.end.append(move)

        old_center_x, old_center_y = self.center_x, self.center_y
        self.reset_pos()

        # The first duck move comes from out of bounds
        if self.board.is_in_bounds(self.piece_pos):
            self.board[self.piece_pos] = None

        self.board[move] = self

        # Move transition is skipped if the piece was dragged to its target by the mouse
        self.start_move_transition(move, old_center_x != self.center_x or old_center_y != self.center_y)

    def start_move_transition(self, move: PiecePos, skip_move_transition: bool) -> None:
        self.clear_moves()

        self.start = arcade.Vec2(int((self.piece_pos.file + 0.5) * PIECE_SIZE), int((self.piece_pos.rank + 0.5) * PIECE_SIZE))
        self.target = arcade.Vec2(int((move.file + 0.5) * PIECE_SIZE), int((move.rank + 0.5) * PIECE_SIZE))

        self.piece_pos = move
        self.moving = True

        if skip_move_transition:
            self.reset_pos()

    def advance_move_transition(self, delta_time: float, view_manager: arcade.Window) -> None:
        cur = arcade.Vec2(self.center_x, self.center_y)
        delta = (self.target - self.start) * delta_time / self.move_transition_length_in_seconds

        if cur.distance(self.target) < delta.length():
            self.end_move_transition(view_manager)
        else:
            self.center_x += delta.x
            self.center_y += delta.y

    def end_move_transition(self, view_manager: arcade.Window) -> None:
        self.reset_pos()
        self.moving = False
        self.just_finished_moving = True

    def fully_end_move_transition(self) -> None:
        self.just_finished_moving = False

    def capture(self, capture: PiecePos):
        if self.board[capture]:
            self.move_packet.captures.append(capture)
            self.board.kill_piece(capture)

        if self.board.has_marker(capture, MarkerPieceType.EN_PASSANT_CASTLE):
            capture = self.board.get_enemy_king_pos(self.piece_color)
            self.move_packet.captures.append(capture)
            self.board.kill_piece(capture)

    def reset_pos(self) -> None:
        self.center_x, self.center_y = int((self.piece_pos.file + 0.5) * PIECE_SIZE), int((self.piece_pos.rank + 0.5) * PIECE_SIZE)

    def draw_as_unselected(self) -> None:
        if self.board.inverted:
            self.center_x, self.center_y = SCREEN_SIZE - self.center_x, SCREEN_SIZE - self.center_y

        sprite_list: arcade.SpriteList[Piece] = arcade.SpriteList()
        sprite_list.append(self)
        sprite_list.draw(pixelated=True)

        if self.board.inverted:
            self.center_x, self.center_y = SCREEN_SIZE - self.center_x, SCREEN_SIZE - self.center_y

    def draw_as_selected(self) -> None:
        for move in self.moves:
            self.draw_move(move)

        for capture in self.captures:
            if self.board.has_marker(capture, MarkerPieceType.EN_PASSANT_CASTLE):
                self.board.draw_markers()

            self.draw_capture(capture)

        self.draw_as_unselected()

    def draw_move(self, move: PiecePos) -> None:
        color = self.move_color(move)

        if self.board.inverted:
            move = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - move

        arcade.draw_circle_filled((move.file + 0.5) * PIECE_SIZE, (move.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 8, color)

    def draw_capture(self, capture: PiecePos) -> None:
        color = self.move_color(capture)

        if self.board.inverted:
            capture = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - capture

        arcade.draw_circle_outline((capture.file + 0.5) * PIECE_SIZE, (capture.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 2, color, PIECE_SCALE * 2)

    def move_color(self, move: PiecePos) -> arcade.types.Color:
        color = arcade.types.Color(0, 0, 0, 128)

        if move in self.illegal_moves:
            color = arcade.types.Color(255, 0, 0)

        return color

    def has_type(self, piece_type: PieceType) -> bool:
        return self.piece_type == piece_type

    def has_color(self, piece_color: PieceColor) -> bool:
        return self.piece_color == piece_color

    def is_friend(self, other: "Piece") -> bool:
        return self.piece_color == other.piece_color or other.piece_color == PieceColor.DUCK

    def is_enemy(self, other: "Piece") -> bool:
        return not self.is_friend(other)

    def __repr__(self) -> str:
        return f" {'N' if self.has_type(PieceType.KNIGHT) else self.piece_type.name[0]}{self.piece_color.name[0]} "