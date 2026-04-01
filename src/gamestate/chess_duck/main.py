from piece.type import PieceType, PieceColor, PiecePos
from piece.piece import Piece
from gamestate.chess_normal.main import ChessNormalMainView
from gamestate.chess_duck.move_duck import MoveDuckView


class ChessDuckMainView(ChessNormalMainView):
    initial_duck_pos: PiecePos = PiecePos.out_of_bounds()

    def __init__(self, *, flip_perspective_on_turn_swap: bool = True) -> None:
        super().__init__(flip_perspective_on_turn_swap=flip_perspective_on_turn_swap)
        self.duck: Piece = self.board.new_piece_of_type(PieceType.PAWN, PieceColor.DUCK, self.initial_duck_pos, add_to_board=False)
        self.duck_move_start: PiecePos = self.initial_duck_pos
        self.duck_move_end: PiecePos = self.initial_duck_pos

    def on_draw(self) -> None:
        super().on_draw()

        self.board.color_tile(self.duck_move_start, self.move_tile_colors[0])
        self.board.color_tile(self.duck_move_end, self.move_tile_colors[1])

        self.duck.draw_as_unselected()

        # Selected piece should appear over the duck
        if self.selected:
            self.selected.draw_as_selected()

    def on_just_ended_move(self) -> None:
        assert(self.selected and self.selected.move_packet)
        self.selected.move_packet.start.append(self.duck.piece_pos)

        self.duck_move_start = self.duck.piece_pos

    def on_fully_ended_move(self) -> None:
        self.window.show_view(MoveDuckView(self))

    def on_fully_ended_duck_move(self, *, call_super: bool = True) -> None:
        assert(self.selected and self.selected.move_packet)
        self.selected.move_packet.end.append(self.duck.piece_pos)

        self.duck_move_end = self.duck.piece_pos

        if call_super:
            super().on_fully_ended_move()