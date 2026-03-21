import arcade
from constants import *
import piece.factory
from piece.piece import Piece, PieceColor, PiecePos


class Board:
    def __init__(self) -> None:
        board = [
            ["RB", "NB", "BB", "QB", "KB", "BB", "NB", "RB"],
            ["PB", "PB", "PB", "PB", "PB", "PB", "PB", "PB"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["PW", "PW", "PW", "PW", "PW", "PW", "PW", "PW"],
            ["RW", "NW", "BW", "QW", "KW", "BW", "NW", "RW"]
        ]

        board = [list(row) for row in board]

        self.pieces: arcade.SpriteList[Piece] = arcade.SpriteList()
        self.board: list[list[Piece | None]] = []

        for rank, row in enumerate(reversed(board)):
            self.board.append([])
            for file, name in enumerate(row):
                if name == "":
                    self.board[-1].append(None)
                else:
                    next_piece = piece.factory.new(name, PiecePos(rank, file))
                    self.pieces.append(next_piece)
                    self.board[-1].append(next_piece)

        self.turn_color: PieceColor = PieceColor.WHITE
        self.future_en_passant: tuple[PiecePos, PieceColor] | None = None

        self.can_castle_kingside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.can_castle_queenside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.selected_rank: int = 0
        self.selected_file: int = 0
        self.selected: Piece | None = None
        self.just_selected: bool = False

        self.gen_moves()

    def update(self, delta_time: float, mouse_x: int, mouse_y: int):
        if not self.selected:
            return

        if self.selected.moving:
            self.selected.advance_move_transition(delta_time)
        elif self.selected.just_finished_moving:
            self.selected.end_move_transition()
            self.selected = None
            self.gen_moves()
        elif self.just_selected:
            self.selected.center_x, self.selected.center_y = mouse_x, mouse_y
        else:
            self.selected.reset_pos()
            

    def draw(self):
        colors = [arcade.color.DARK_MOSS_GREEN, arcade.color.FLORAL_WHITE]

        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                arcade.draw_lbwh_rectangle_filled(file * PIECE_SIZE, rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, colors[(rank + file) % 2])
                if self.selected and rank == self.selected_rank and file == self.selected_file:
                    arcade.draw_lbwh_rectangle_filled(file * PIECE_SIZE, rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, (255, 255, 0, 128))

        self.pieces.draw(pixelated=True)

        if self.selected:
            self.selected.draw_as_selected()

    def gen_moves(self) -> None:
        for piece in self.pieces:
            if piece.has_color(self.turn_color):
                piece.gen_moves(self.board, self.future_en_passant, self.can_castle_kingside[self.turn_color], self.can_castle_queenside[self.turn_color])

    def on_left_click_press(self, x: int, y: int) -> None:
        if self.selected and self.selected.moving:
            return

        rank, file = self.to_rank_file(x, y)

        if self.is_in_bounds(rank, file) and (piece := self.board[rank][file]) and piece.has_color(self.turn_color):
            self.selected_rank, self.selected_file = rank, file
            self.selected = piece
            self.just_selected = True

    def on_left_click_release(self, x: int, y: int) -> None:
        if not self.selected or self.selected.moving:
            return

        move = PiecePos(*self.to_rank_file(x, y))
        move_result = self.selected.try_move(self.board, move)

        if move_result.did_move:
            self.future_en_passant = move_result.future_en_passant

            if move_result.disable_kingside_castle:
                self.can_castle_kingside[self.turn_color] = False

            if move_result.disable_queenside_castle:
                self.can_castle_queenside[self.turn_color] = False

            self.turn_color = PieceColor.WHITE if self.turn_color == PieceColor.BLACK else PieceColor.BLACK
        elif not self.just_selected:
            self.selected.reset_pos()
            self.selected = None

        self.just_selected = False

    def is_in_bounds(self, rank: int, file: int) -> bool:
        return 0 <= rank < BOARD_SIZE and 0 <= file < BOARD_SIZE

    @staticmethod
    def to_rank_file(x: int, y: int) -> tuple[int, int]:
        return int(y // PIECE_SIZE), int(x // PIECE_SIZE)