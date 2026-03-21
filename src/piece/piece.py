import arcade
from constants import *
from .type import *


class Piece(arcade.Sprite):
    move_transition_length_in_seconds = 0.125

    def __init__(self, piece_type: PieceType, piece_color: PieceColor, piece_pos: PiecePos, dirs: set[PiecePos] | None = None, /, symmetric_dirs: bool = True) -> None:
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

        self.moves: set[PiecePos] = set()
        self.captures: set[PiecePos] = set()

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
    def try_add_move(self, board: list[list["Piece | None"]], pos: PiecePos, dir: PiecePos, /, allow_move: bool = True, allow_capture: bool = True) -> bool:
        move = pos + dir
        try:
            piece = board[move.rank][move.file]
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

    def gen_moves(self, board: list[list["Piece | None"]], en_passant: tuple[PiecePos, PieceColor] | None, can_castle_kingside: bool, can_castle_queenside: bool) -> None:
        self.clear_moves()

    def clear_moves(self) -> None:
        self.moves = set()
        self.captures = set()

    class MoveResult:
        def __init__(self, did_move: bool, future_en_passant: tuple[PiecePos, PieceColor] | None = None, disable_kingside_castle: bool = False, disable_queenside_castle: bool = False) -> None:
            self.did_move = did_move
            self.future_en_passant = future_en_passant
            self.disable_kingside_castle = disable_kingside_castle
            self.disable_queenside_castle = disable_queenside_castle

    def try_move(self, board: list[list["Piece | None"]], move: PiecePos) -> MoveResult:
        can_move = move in self.moves
        can_capture = move in self.captures

        if can_move or can_capture:
            if can_capture:
                self.capture(board, move)

            self.move(board, move)

            return self.MoveResult(True)

        return self.MoveResult(False)

    def move(self, board: list[list["Piece | None"]], move: PiecePos) -> None:
        old_center_x, old_center_y = self.center_x, self.center_y
        self.reset_pos()

        board[move.rank][move.file] = self
        board[self.piece_pos.rank][self.piece_pos.file] = None

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

    def advance_move_transition(self, delta_time: float) -> None:
        cur = arcade.Vec2(self.center_x, self.center_y)
        delta = (self.target - self.start) * delta_time / self.move_transition_length_in_seconds

        if cur.distance(self.target) < delta.length():
            self.end_move_transition()
        else:
            self.center_x += delta.x
            self.center_y += delta.y

    def end_move_transition(self) -> None:
        self.reset_pos()
        self.moving = False
        self.just_finished_moving = not self.just_finished_moving

    def capture(self, board: list[list["Piece | None"]], move: PiecePos):
        assert(victim := board[move.rank][move.file])
        victim.remove_from_sprite_lists()
        board[move.rank][move.file] = None

    def reset_pos(self) -> None:
        self.center_x, self.center_y = int((self.piece_pos.file + 0.5) * PIECE_SIZE), int((self.piece_pos.rank + 0.5) * PIECE_SIZE)

    def draw_as_selected(self) -> None:
        for move in self.moves:
            self.draw_move(move)

        for capture in self.captures:
            self.draw_capture(capture)

        sprite_list: arcade.SpriteList[Piece] = arcade.SpriteList()
        sprite_list.append(self)
        sprite_list.draw(pixelated=True)

    @staticmethod
    def draw_move(move: PiecePos):
        arcade.draw_circle_filled((move.file + 0.5) * PIECE_SIZE, (move.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 8, (0, 0, 0, 128))

    @staticmethod
    def draw_capture(move: PiecePos):
        arcade.draw_circle_outline((move.file + 0.5) * PIECE_SIZE, (move.rank + 0.5) * PIECE_SIZE, PIECE_SIZE // 2, (0, 0, 0, 128), PIECE_SCALE * 2)

    def has_type(self, piece_type: PieceType) -> bool:
        return self.piece_type == piece_type

    def has_color(self, piece_color: PieceColor) -> bool:
        return self.piece_color == piece_color

    def is_enemy(self, other: "Piece"):
        return self.piece_color != other.piece_color