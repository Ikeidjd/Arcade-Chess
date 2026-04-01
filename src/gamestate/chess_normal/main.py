import arcade
from constants import SCREEN_SIZE, BOARD_SIZE
from board import Board
from gamestate.menu.main import MenuMainView
from piece.piece import Piece, PieceColor, PiecePos


class ChessNormalMainView(arcade.View):
    initial_board: list[list[str]] = [
        ["RB", "NB", "BB", "QB", "KB", "BB", "NB", "RB"],
        ["PB", "PB", "PB", "PB", "PB", "PB", "PB", "PB"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["PW", "PW", "PW", "PW", "PW", "PW", "PW", "PW"],
        ["RW", "NW", "BW", "QW", "KW", "BW", "NW", "RW"]
    ]

    move_tile_colors = [arcade.types.Color(255, 255, 0, 128), arcade.types.Color(255, 255, 0, 160)]

    def __init__(self, initial_board: list[list[str]] | None = None, *, flip_perspective_on_turn_swap: bool = True, allow_illegal_moves: bool = False) -> None:
        super().__init__()

        self.flip_perspective_on_turn_swap: bool = flip_perspective_on_turn_swap
        self.allow_illegal_moves: bool = allow_illegal_moves

        self.board: Board[Piece] = Board(self.initial_board if initial_board is None else initial_board)
        self.last_move: tuple[PiecePos, PiecePos] | None = None
        self.cur_turn_color: PieceColor = PieceColor.WHITE

        self.selected_pos: PiecePos = PiecePos(0, 0)
        self.selected: Piece | None = None
        self.just_selected: bool = False

        self.can_castle_kingside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.can_castle_queenside: dict[PieceColor, bool] = {
            PieceColor.WHITE: True,
            PieceColor.BLACK: True
        }

        self.gen_moves()

        self.mouse_x: int = 0
        self.mouse_y: int = 0

        self.camera = arcade.Camera2D(arcade.LBWH(self.window.center_x - SCREEN_SIZE * 0.5, self.window.center_y - SCREEN_SIZE * 0.5, SCREEN_SIZE, SCREEN_SIZE))

    def on_update(self, delta_time: float) -> None:
        if not self.selected:
            return

        if self.selected.moving:
            self.selected.advance_move_transition(delta_time, self.window)
        elif self.selected.just_finished_moving:
            self.on_fully_ended_move()
        elif self.just_selected:
            self.selected.center_x, self.selected.center_y = self.mouse_x, self.mouse_y
        else:
            self.selected.reset_pos()

        if self.selected and self.selected.just_finished_moving:
            self.on_just_ended_move()

    def gen_moves(self) -> None:
        for piece in self.board.pieces:
            if piece.has_color(self.cur_turn_color):
                piece.gen_moves(self.can_castle_kingside[self.cur_turn_color], self.can_castle_queenside[self.cur_turn_color])

                for move in piece.simulate_moves():
                    if self.is_in_check():
                        piece.add_illegal_move(move, allow_illegal_moves=self.allow_illegal_moves)

    def is_in_check(self) -> bool:
        self.half_swap_turn()

        for piece in self.board.pieces:
            if piece.has_color(self.cur_turn_color):
                piece.gen_moves(self.can_castle_kingside[self.cur_turn_color], self.can_castle_queenside[self.cur_turn_color])

                if piece.gives_check():
                    self.half_swap_turn()
                    return True

        self.half_swap_turn()
        return False

    def on_just_ended_move(self) -> None:
        pass

    def on_fully_ended_move(self) -> None:
        assert(self.selected)

        self.selected.fully_end_move_transition()
        self.selected = None

        self.board.advance_markers()
        self.swap_turn()
        self.gen_moves()

    def on_draw(self) -> None:
        # self.camera.use()
        self.board.draw_background()

        if self.selected:
            self.board.color_tile(self.selected.piece_pos, self.move_tile_colors[0])

        if self.last_move:
            self.board.color_tile(self.last_move[0], self.move_tile_colors[0])
            self.board.color_tile(self.last_move[1], self.move_tile_colors[1])

        self.board.draw_pieces()

        if self.selected:
            self.selected.draw_as_selected()

    def half_swap_turn(self) -> None:
        self.cur_turn_color = PieceColor.WHITE if self.cur_turn_color == PieceColor.BLACK else PieceColor.BLACK

    def swap_turn(self) -> None:
        self.half_swap_turn()

        if self.flip_perspective_on_turn_swap:
            self.board.inverted = not self.board.inverted
            self.mouse_x, self.mouse_y = SCREEN_SIZE - self.mouse_x, SCREEN_SIZE - self.mouse_y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        x -= int(self.camera.viewport.left)
        y -= int(self.camera.viewport.bottom)

        if button != arcade.MOUSE_BUTTON_LEFT or self.selected and self.selected.moving:
            return

        pos = self.board.to_piece_pos(x, y)

        if self.board.is_in_bounds(pos) and (piece := self.board[pos]) and piece.has_color(self.cur_turn_color):
            self.selected_pos = pos
            self.selected = piece
            self.just_selected = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        x -= int(self.camera.viewport.left)
        y -= int(self.camera.viewport.bottom)

        if button != arcade.MOUSE_BUTTON_LEFT or not self.selected or self.selected.moving:
            return

        move = self.board.to_piece_pos(x, y)
        move_result = self.selected.try_move(move)

        if move_result.did_move:
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
        x -= int(self.camera.viewport.left)
        y -= int(self.camera.viewport.bottom)

        self.mouse_x = x + dx
        self.mouse_y = y + dy

        if self.board.inverted:
            self.mouse_x, self.mouse_y = SCREEN_SIZE - self.mouse_x, SCREEN_SIZE - self.mouse_y

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(MenuMainView())