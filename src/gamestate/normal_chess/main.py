import arcade
from constants import PIECE_SIZE
from board import Board
from piece.piece import Piece, PieceColor, PiecePos


class NormalChessMainView(arcade.View):
    move_tile_colors = [arcade.types.Color(255, 255, 0, 128), arcade.types.Color(255, 255, 0, 160)]

    def __init__(self) -> None:
        super().__init__()

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

        self.board: Board[Piece] = Board(board)
        self.last_move: tuple[PiecePos, PiecePos] | None = None
        self.cur_turn_color: PieceColor = PieceColor.WHITE

        self.selected_pos: PiecePos = PiecePos(0, 0)
        self.selected: Piece | None = None
        self.just_selected: bool = False

        self.future_en_passant_pos: PiecePos | None = None

        self.can_castle_kingside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.can_castle_queenside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.mouse_x: int = 0
        self.mouse_y: int = 0

        self.gen_moves()

    def on_update(self, delta_time: float) -> None:
        if not self.selected:
            return

        if self.selected.moving:
            self.selected.advance_move_transition(delta_time, self.window)
        elif self.selected.just_finished_moving:
            self.selected.fully_end_move_transition()
            self.selected = None
            self.swap_turn()
            self.gen_moves()
        elif self.just_selected:
            self.selected.center_x, self.selected.center_y = self.mouse_x, self.mouse_y
        else:
            self.selected.reset_pos()

    def gen_moves(self) -> None:
        for piece in self.board.pieces: # type: ignore
            if piece.has_color(self.cur_turn_color): # type: ignore
                piece.gen_moves(self.future_en_passant_pos, self.can_castle_kingside[self.cur_turn_color], self.can_castle_queenside[self.cur_turn_color]) # type: ignore

    def on_draw(self) -> None:
        self.board.draw_background()

        if self.selected:
            arcade.draw_lbwh_rectangle_filled(self.selected.piece_pos.file * PIECE_SIZE, self.selected.piece_pos.rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, self.move_tile_colors[0])
            self.selected.draw_as_selected()

        if self.last_move:
            arcade.draw_lbwh_rectangle_filled(self.last_move[0].file * PIECE_SIZE, self.last_move[0].rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, self.move_tile_colors[0])
            arcade.draw_lbwh_rectangle_filled(self.last_move[1].file * PIECE_SIZE, self.last_move[1].rank * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE, self.move_tile_colors[1])

        self.board.draw_pieces()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT or self.selected and self.selected.moving:
            return

        pos = self.board.to_piece_pos(x, y)

        if self.board.is_in_bounds(pos) and (piece := self.board[pos]) and piece.has_color(self.cur_turn_color):
            self.selected_pos = pos
            self.selected = piece
            self.just_selected = True

    def swap_turn(self) -> None:
        self.cur_turn_color = PieceColor.WHITE if self.cur_turn_color == PieceColor.BLACK else PieceColor.BLACK

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT or not self.selected or self.selected.moving:
            return

        move = self.board.to_piece_pos(x, y)
        move_result = self.selected.try_move(move)

        if move_result.did_move:
            self.future_en_passant_pos = move_result.future_en_passant_pos

            if move_result.disable_kingside_castle:
                self.can_castle_kingside[self.cur_turn_color] = False

            if move_result.disable_queenside_castle:
                self.can_castle_queenside[self.cur_turn_color] = False

            self.last_move = (self.selected_pos, move)
        elif not self.just_selected:
            self.selected.reset_pos()
            self.selected = None

        self.just_selected = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x + dx
        self.mouse_y = y + dy