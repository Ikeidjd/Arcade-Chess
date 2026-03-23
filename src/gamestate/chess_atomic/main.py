from piece.type import PieceType, PiecePos
from gamestate.chess_normal.main import ChessNormalMainView


class ChessAtomicMainView(ChessNormalMainView):
    def __init__(self, /, flip_perspective_on_turn_swap: bool = True) -> None:
        super().__init__(flip_perspective_on_turn_swap=flip_perspective_on_turn_swap)

    def on_fully_ended_move(self, /, call_super: bool = True) -> None:
        assert(self.selected)

        if self.selected.move_packet.captures:
            captures = self.selected.move_packet.captures.copy()

            for capture in captures:
                for rank in range(-1, 2):
                    for file in range(-1, 2):
                        pos = capture + PiecePos(rank, file)

                        if not self.board.is_in_bounds(pos) or pos == capture or not (piece := self.board[pos]) or piece.piece_type == PieceType.PAWN:
                            continue

                        self.selected.move_packet.captures.append(pos)
                        self.board.kill_piece(pos)

        if call_super:
            super().on_fully_ended_move()