import arcade
from constants import BOARD_SIZE
from board import Board
from piece.piece import Piece
from piece.type import PiecePos


class MoveDuckView(arcade.View):
    def __init__(self, prev_view: arcade.View) -> None:
        super().__init__()

        from gamestate.chess_duck.main import ChessDuckMainView
        assert(isinstance(prev_view, ChessDuckMainView))

        self.prev_view: ChessDuckMainView = prev_view
        self.board: Board[Piece] = self.prev_view.board
        self.duck: Piece = self.prev_view.duck

    def on_update(self, delta_time: float) -> None:
        if self.duck.moving:
            self.duck.advance_move_transition(delta_time, self.window)
        elif self.duck.just_finished_moving:
            self.duck.fully_end_move_transition()
            self.window.show_view(self.prev_view)
            self.prev_view.on_fully_ended_duck_move()

    def on_draw(self) -> None:
        self.board.draw_everything()

        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                pos = PiecePos(rank, file)
                piece = self.board[pos]

                if piece is None:
                    self.duck.draw_move(pos)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.duck.moving or self.duck.just_finished_moving:
            return

        move = self.board.to_piece_pos(x, y)
        piece = self.board[move]

        if piece is None:
            self.duck.move(move)