import arcade
from constants import *
from gamestate.chess_normal.move_packet import MovePacket
from .type import *
from board import Board


class Piece(arcade.Sprite):
    move_transition_length_in_seconds = 0.125

    def __init__(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, board: Board["Piece"], dirs: set[PiecePos] | None = None, /, symmetric_dirs: bool = True) -> None:
        self.piece_type: PieceType = piece_type
        self.piece_color: PieceColor = piece_color
        self.piece_pos: PiecePos = piece_pos

        super().__init__(piece_sprite_paths[self.piece_color][self.piece_type], PIECE_SCALE)
        self.reset_pos()

        if dirs:
            self.dirs: set[PiecePos] = dirs
        else:
            self.dirs = set()

        if symmetric_dirs:
            self.make_dirs_symmetric()

        self.board = board

        self.moves: set[PiecePos] = set()
        self.captures: set[PiecePos] = set()

        self.move_packet = MovePacket(self.piece_color)

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

    # Returns false if a move (not capture) was possible
    def try_add_move(self, pos: PiecePos, dir: PiecePos, /, allow_move: bool = True, allow_capture: bool = True) -> bool:
        move = pos + dir
        try:
            piece = self.board[move]
        except IndexError:
            return False
        else:
            if piece is None:
                if allow_move:
                    self.moves.add(move)
                    return True
                return False

            if allow_capture and self.is_enemy(piece):
                self.captures.add(move)

            return False

    def gen_moves(self, possible_en_passant_pos: PiecePos | None, can_castle_kingside: bool, can_castle_queenside: bool) -> None:
        self.clear_moves()
        self.move_packet = MovePacket(self.piece_color)

    def clear_moves(self) -> None:
        self.moves = set()
        self.captures = set()

    class MoveResult:
        def __init__(self, did_move: bool, future_en_passant_pos: PiecePos | None = None, disable_kingside_castle: bool = False, disable_queenside_castle: bool = False) -> None:
            self.did_move = did_move
            self.future_en_passant_pos = future_en_passant_pos
            self.disable_kingside_castle = disable_kingside_castle
            self.disable_queenside_castle = disable_queenside_castle

    def try_move(self, move: PiecePos) -> MoveResult:
        can_move = move in self.moves
        can_capture = move in self.captures

        if can_move or can_capture:
            if can_capture:
                self.capture(move)

            self.move(move)

            return self.MoveResult(True)

        return self.MoveResult(False)

    def move(self, move: PiecePos) -> None:
        self.move_packet.start.append(self.piece_pos)
        self.move_packet.end.append(move)

        old_center_x, old_center_y = self.center_x, self.center_y
        self.reset_pos()

        self.board[move] = self
        self.board[self.piece_pos] = None

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

    def capture(self, move: PiecePos):
        self.move_packet.capture = move
        self.board.kill_piece(move)

    def reset_pos(self) -> None:
        self.center_x, self.center_y = int((self.piece_pos.file + 0.5) * PIECE_SIZE), int((self.piece_pos.rank + 0.5) * PIECE_SIZE)

    def draw_as_selected(self) -> None:
        for move in self.moves:
            self.draw_move(move)

        for capture in self.captures:
            self.draw_capture(capture)

        if self.board.inverted:
            self.center_x, self.center_y = SCREEN_SIZE - self.center_x, SCREEN_SIZE - self.center_y

        sprite_list: arcade.SpriteList[Piece] = arcade.SpriteList()
        sprite_list.append(self)
        sprite_list.draw(pixelated=True)

        if self.board.inverted:
            self.center_x, self.center_y = SCREEN_SIZE - self.center_x, SCREEN_SIZE - self.center_y

    def has_type(self, piece_type: PieceType) -> bool:
        return self.piece_type == piece_type

    def has_color(self, piece_color: PieceColor) -> bool:
        return self.piece_color == piece_color

    def is_enemy(self, other: "Piece"):
        return self.piece_color != other.piece_color

    def draw_move(self, move: PiecePos):
        if self.board.inverted:
            move = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - move

        arcade.draw_circle_filled((move.file + 0.5) * PIECE_SIZE, (move.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 8, (0, 0, 0, 128))

    def draw_capture(self, capture: PiecePos):
        if self.board.inverted:
            capture = PiecePos(BOARD_SIZE - 1, BOARD_SIZE - 1) - capture

        arcade.draw_circle_outline((capture.file + 0.5) * PIECE_SIZE, (capture.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 2, (0, 0, 0, 128), PIECE_SCALE * 2)